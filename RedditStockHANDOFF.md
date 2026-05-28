# HANDOFF: Reddit Sentiment Stock Tracker

## What This Project Is
A full-stack web app that scrapes Reddit financial communities (r/wallstreetbets, r/stocks, r/investing),
performs NLP sentiment analysis on posts/comments, extracts stock ticker mentions, correlates sentiment
with real price data, and visualizes trends on a dashboard. The goal is a resume project showcasing:
NLP, data pipelines, full-stack dev, and real financial data — similar structure to ValReader.

---

## What Has Been Done So Far

### Phase 1: Data Pipeline — COMPLETE

All backend pipeline files are built and tested end-to-end against live Reddit data and MongoDB Atlas.

**Key deviation from original plan:** Reddit's standard Data API now requires approval that is heavily restricted for hobbyist projects. Switched to Reddit's **public JSON API** (no credentials needed) via `requests`. Same data, zero auth friction.

**Files built:**
- `backend/scraper.py` — polls Reddit's public `.json` endpoints (no API key needed), 2s delay between requests to respect rate limits
- `backend/tickers.py` — regex extraction + S&P 500 ticker validation downloaded from GitHub datasets. Includes blacklist for common false positives (IT, NOW, ARE, etc.)
- `backend/sentiment.py` — VADER scoring on combined title + body text, returns compound score (-1 to +1) and bullish/bearish/neutral label
- `backend/db.py` — MongoDB Atlas connection via pymongo, 3 collections: `posts`, `ticker_snapshots`, `prices`, with upsert helpers and indexes
- `backend/prices.py` — yfinance wrapper with try/except, returns hourly close + volume
- `backend/scheduler.py` — APScheduler running full pipeline every 30 min, also the entry point (`python scheduler.py`)
- `backend/requirements.txt` — pinned dependencies
- `.env.example` — template (only MONGODB_URI needed now)
- `.gitignore` — excludes .env, __pycache__, backend/data/

**Infrastructure:**
- MongoDB Atlas M0 free cluster: `kalereddittrader.0hiy6zq.mongodb.net`, database `sentiment_trader`
- `.env` file at project root with MONGODB_URI (not committed)
- S&P 500 ticker CSV auto-downloaded to `backend/data/sp500_tickers.csv` on first run (gitignored)

**Verified working:** Scraped live WSB posts, extracted tickers (NVDA, MU, META, DELL, MSFT), scored sentiment, stored in MongoDB Atlas.

---

## Agreed Architecture

### Tech Stack
| Layer | Choice | Reason |
|---|---|---|
| Scraping | `requests` → Reddit public JSON API | Reddit API approval heavily restricted; public .json endpoints require no auth |
| Sentiment | `VADER` first, upgrade to `FinBERT` later | VADER is fast/easy; FinBERT is finance-tuned for better accuracy |
| Ticker extraction | `regex` + S&P 500 CSV | Match $TICKER patterns, filter against known ticker list |
| Price data | `yfinance` (Yahoo Finance) | Free, no API key needed, easy Python library |
| Backend | `FastAPI` (Python) | Lightweight, async-friendly, easy REST endpoints |
| Database | `MongoDB` (via `pymongo`) | Matches user's existing experience from ValReader |
| Frontend | `React` + `Recharts` | Matches user's existing experience; Recharts for stock/sentiment charts |
| Alerting (optional) | `discord.py` bot | Pings a Discord channel when ticker mention volume spikes |

---

## Project Structure
```
Reddit-Stock-Tracker/
├── backend/
│   ├── scraper.py            # Reddit public JSON API scraper (no auth needed)
│   ├── sentiment.py          # VADER sentiment scoring
│   ├── tickers.py            # Ticker extraction + S&P 500 validation
│   ├── prices.py             # yfinance price fetching
│   ├── db.py                 # MongoDB connection + queries
│   ├── scheduler.py          # APScheduler pipeline runner + entry point
│   └── requirements.txt
├── frontend/                 # NOT YET BUILT (Phase 3)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── TickerCard.jsx
│   │   │   ├── SentimentChart.jsx
│   │   │   ├── PriceOverlay.jsx
│   │   │   ├── TrendingTickers.jsx
│   │   │   └── HeatMap.jsx
│   │   └── api.js
│   └── package.json
├── bot/
│   └── alert_bot.py          # Optional Discord bot (Phase 4)
├── .env                      # NOT committed — contains MONGODB_URI
├── .env.example              # Template
├── .gitignore
└── RedditStockHANDOFF.md
```

---

## Build Order Progress

### Phase 1: Data Pipeline — COMPLETE
See "What Has Been Done So Far" above.

### Phase 2: FastAPI Backend — UP NEXT
Build `backend/main.py` with these endpoints:

| Method | Route | Returns |
|---|---|---|
| GET | `/tickers/trending` | Top 10 tickers by mention count (last 24h) |
| GET | `/tickers/{symbol}/sentiment` | Sentiment scores over time for one ticker |
| GET | `/tickers/{symbol}/price` | Price history for one ticker |
| GET | `/tickers/{symbol}/combined` | Sentiment + price in one response for chart overlay |
| GET | `/feed` | Latest 50 scraped posts with tickers + scores |

Start the server with: `uvicorn main:app --reload` from the `backend/` directory.
Remember to add CORS middleware or the React frontend won't be able to call it.

### Phase 3: React Frontend — NOT STARTED
Build in this order:
1. `TrendingTickers.jsx` — ranked list of hottest tickers, fetch from `/tickers/trending`
2. `SentimentChart.jsx` — Recharts `<LineChart>` of sentiment score over time
3. `PriceOverlay.jsx` — second Y-axis on same chart showing price, fetch from `/combined`
4. `TickerCard.jsx` — wrap charts into a card with bullish/bearish/neutral label
5. `App.jsx` — search bar to look up any ticker + trending feed

### Phase 4: Optional Upgrades
- **Swap VADER → FinBERT** — `ProsusAI/finbert` on HuggingFace for finance-tuned accuracy
- **Discord alert bot** — ping when ticker mention volume spikes 3x average
- **Correlation score** — Pearson correlation between 24h sentiment and next-day price delta

---

## Key Gotchas / Things to Watch Out For

1. **Reddit public JSON rate limits** — 2s delay between requests is safe; do not remove it
2. **Ticker false positives** — words like "IT", "NOW", "ARE" are valid tickers; blacklist in `tickers.py` handles this
3. **VADER is not finance-tuned** — "sick gains" scores negative with VADER. Note this limitation in the README; FinBERT is Phase 4
4. **yfinance can be flaky** — already wrapped in try/except; MongoDB upsert deduplicates so re-fetching is safe
5. **MongoDB free tier** — 512MB, currently using ~112MB baseline overhead (not real data). Plenty of headroom.
6. **CORS** — add `fastapi.middleware.cors` to `main.py` before building the frontend

---

## Environment Variables Needed (.env)
```
MONGODB_URI=mongodb+srv://...
```
Reddit credentials are NOT needed — using public JSON API.

---

## How to Frame This on a Resume
- Built a full-stack sentiment analysis platform that scrapes Reddit financial communities, extracts stock ticker mentions via NLP, and correlates crowd sentiment with real-time price data via the Yahoo Finance API
- Designed a React dashboard with overlaid sentiment/price charts using Recharts, backed by a FastAPI REST API and MongoDB for time-series storage
- Implemented automated data pipeline with 30-minute scheduled scraping intervals and optional Discord alerting on unusual ticker mention spikes

---

## Next Agent Instructions
1. Load this file — it is the single source of truth
2. Phase 1 is complete — do not rebuild it
3. Start Phase 2: build `backend/main.py` with the 5 FastAPI endpoints listed above
4. Run `uvicorn main:app --reload` from `backend/` and test all endpoints with curl or Postman
5. Add CORS middleware before any frontend work
6. Build Phase 3 (React) only after all API endpoints are verified working
