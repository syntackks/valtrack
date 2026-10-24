# VALTRACK

A tracker.gg-style VALORANT stats lookup app. Search any Riot ID and see their
current rank and recent match history. Built with Flask + the community
HenrikDev API.

Not affiliated with Riot Games. This is a learning/portfolio project.

## Setup

1. **Get a free API key**
   Go to the [HenrikDev API dashboard](https://api.henrikdev.xyz/dashboard/),
   sign in, open **API Keys** in the sidebar, and generate a **Basic** key.

2. **Clone/copy this project, then create a virtual environment**
   ```bash
   cd valtrack
   python3 -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API key**
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and paste your key in place of `your_key_here`.

5. **Run it**
   ```bash
   python app.py
   ```
   Open **http://127.0.0.1:5000** in your browser.

6. **Try a search**
   Enter any Riot ID in the form `Name#Tag` (e.g. `Phoenix#1234`), pick the
   right region, and hit search.

## Project structure

```
valtrack/
├── app.py              # Flask routes
├── valorant_api.py      # HenrikDev API wrapper + match-data helpers
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html
│   ├── index.html       # search page
│   └── results.html     # player card + match history
└── static/
    └── style.css
```

## Notes & gotchas

- **Rate limits**: a Basic key allows 30 requests/minute. Each search makes
  3 calls (account, MMR, matches), so don't spam the search box.
- **Region matters**: HenrikDev needs the correct region (na/eu/ap/kr/latam/br)
  to find a player — if a search 404s, try a different region.
- **Riot ID format**: must include the `#tag` — e.g. `Phoenix#1234`, not just
  `Phoenix`.
- **Deploying**: this app reads `HENRIK_API_KEY` from the environment, so on
  a host like Render or PythonAnywhere, set it as an environment variable in
  their dashboard instead of uploading your `.env` file.

## Ideas for extending this

- Cache recent lookups so repeat searches don't burn API calls.
- Add a "team" page: save a list of Riot IDs and show everyone's stats
  together (nice fit for a squad like DivisionGG).
- Add per-agent stats or a win-rate chart using recharts/Chart.js.
- Add match detail pages (click a match row to see the full scoreboard).
