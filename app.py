import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

from valorant_api import ValorantAPI, ValorantAPIError, summarize_match

load_dotenv()

app = Flask(__name__)

REGIONS = [
    ("na", "North America"),
    ("eu", "Europe"),
    ("ap", "Asia Pacific"),
    ("kr", "Korea"),
    ("latam", "Latin America"),
    ("br", "Brazil"),
]


@app.route("/")
def index():
    return render_template("index.html", regions=REGIONS)


@app.route("/player")
def player():
    riot_id = request.args.get("riot_id", "").strip()
    region = request.args.get("region", "na").strip()

    if "#" not in riot_id:
        return render_template(
            "index.html",
            regions=REGIONS,
            error="Enter a Riot ID in the form Name#Tag (e.g. Phoenix#1234).",
        )

    name, tag = riot_id.split("#", 1)
    name, tag = name.strip(), tag.strip()

    try:
        api = ValorantAPI()
        account = api.get_account(name, tag)
        mmr = api.get_mmr(region, name, tag)
        raw_matches = api.get_matches(region, name, tag, size=5)
    except ValorantAPIError as exc:
        return render_template("index.html", regions=REGIONS, error=str(exc))

    matches = []
    for m in raw_matches:
        summary = summarize_match(m, name, tag)
        if summary:
            matches.append(summary)

    return render_template(
        "results.html",
        account=account,
        mmr=mmr,
        matches=matches,
        region=region,
        riot_name=name,
        riot_tag=tag,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
