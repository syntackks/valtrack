"""
Thin wrapper around the HenrikDev unofficial VALORANT API.
Docs: https://docs.henrikdev.xyz/valorant

This API is community-run and not affiliated with Riot Games. Be a good
citizen: keep request volume reasonable and don't hammer it in a loop.
"""

import os
import requests

BASE_URL = "https://api.henrikdev.xyz"


class ValorantAPIError(Exception):
    """Raised when the API returns an error or an unexpected response."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class ValorantAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("HENRIK_API_KEY")
        if not self.api_key:
            raise ValorantAPIError(
                "No HenrikDev API key found. Set HENRIK_API_KEY in your .env file."
            )

    def _get(self, path, params=None):
        url = f"{BASE_URL}{path}"
        headers = {"Authorization": self.api_key}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        except requests.RequestException as exc:
            raise ValorantAPIError(f"Network error contacting HenrikDev API: {exc}")

        if resp.status_code == 404:
            raise ValorantAPIError("Player or match not found. Double-check the Riot ID and region.", 404)
        if resp.status_code == 429:
            raise ValorantAPIError("Rate limit hit — wait a bit before trying again.", 429)
        if resp.status_code == 403:
            raise ValorantAPIError("Request blocked (Riot maintenance or bot protection). Try again shortly.", 403)
        if not resp.ok:
            raise ValorantAPIError(f"HenrikDev API returned an error (status {resp.status_code}).", resp.status_code)

        payload = resp.json()
        if payload.get("data") is None:
            raise ValorantAPIError("No data returned for that player.")
        return payload["data"]

    def get_account(self, name, tag):
        """Basic account info: puuid, account level, card art, region."""
        return self._get(f"/valorant/v1/account/{name}/{tag}")

    def get_mmr(self, region, name, tag):
        """Current rank, RR, and last-game RR change."""
        return self._get(f"/valorant/v2/mmr/{region}/{name}/{tag}")

    def get_matches(self, region, name, tag, size=5, platform="pc"):
        """Recent match history (default: 5 most recent matches)."""
        data = self._get(
            f"/valorant/v4/matches/{region}/{platform}/{name}/{tag}",
            params={"size": size},
        )
        return data


def summarize_match(match, riot_name, riot_tag):
    """
    Pull out the bits we care about for one match, for the given player,
    from a raw v4 match object.
    """
    meta = match.get("metadata", {})
    players = match.get("players", [])
    teams = match.get("teams", [])

    me = next(
        (p for p in players if p.get("name", "").lower() == riot_name.lower()
         and p.get("tag", "").lower() == riot_tag.lower()),
        None,
    )
    if me is None:
        return None

    stats = me.get("stats", {})
    team_id = me.get("team_id")
    team_info = next((t for t in teams if t.get("team_id") == team_id), None)
    won = bool(team_info.get("won")) if team_info else None

    kills = stats.get("kills", 0)
    deaths = stats.get("deaths", 0)
    assists = stats.get("assists", 0)
    kd = round(kills / deaths, 2) if deaths else float(kills)

    return {
        "map": meta.get("map", {}).get("name", "Unknown"),
        "mode": meta.get("queue", {}).get("name", "Unknown"),
        "agent": me.get("agent", {}).get("name", "Unknown"),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kd": kd,
        "score": stats.get("score", 0),
        "won": won,
        "rounds_won": team_info.get("rounds", {}).get("won") if team_info else None,
        "rounds_lost": team_info.get("rounds", {}).get("lost") if team_info else None,
        "started_at": meta.get("started_at"),
    }
