# HANDOFF: Reddit Sentiment Stock Tracker

## What This Project Is
A full-stack web app that scrapes financial social media (originally Reddit, now StockTwits — see below),
performs NLP sentiment analysis on posts, extracts stock ticker mentions, correlates sentiment with real
price data, and visualizes trends on a dashboard. Resume project showcasing NLP, data pipelines,
full-stack dev, and real financial data.

---

## Critical Context: Data Source History

### What We Tried With Reddit (DO NOT RETRY)

Three approaches were attempted in order. All failed. Do not revisit any of these.

1. **Reddit Data API (PRAW)** — Requires app approval. Reddit now heavily restricts hobbyist/personal
   projects. Approval was denied. Abandoned.

2. **Reddit public JSON API** (`https://www.reddit.com/r/wallstreetbets/hot.json`) — No credentials
   needed. Worked during Phase 1 testing (May 27). By May 29, Reddit began returning **403 Blocked**
   on all requests regardless of User-Agent. Abandoned.

3. **old.reddit.com JSON** (`https://old.reddit.com/r/wallstreetbets/hot.json`) — Same result,
   immediate 403. Abandoned.

### Current Data Source: StockTwits
Switched to the **StockTwits public API** (no auth required for basic streams).
- `https://api.stocktwits.com/api/2/streams/trending.json` — trending tickers with messages
- `https://api.stocktwits.com/api/2/streams/symbol/{SYMBOL}.json` — per-symbol message stream (30 msgs)
- Returns up to 30 messages per symbol per request
- 1s delay between requests is safe
- No API key needed
- StockTwits is finance-specific — no false positive ticker words like "IT" or "NOW"
- Messages use `$TICKER` cashtag format, which the existing `tickers.py` extractor already handles

The scraper output format is identical to the old Reddit scraper so **nothing else in the pipeline
changed**. `scheduler.py`, `tickers.py`, `sentiment.py`, `db.py`, and `prices.py` are all untouched.

---

## Current State of All Phases

### Phase 1: Data Pipeline — COMPLETE (scraper rewritten to StockTwits)

**Files:**
- `backend/scraper.py` — StockTwits scraper. Fetches trending symbols, then messages per symbol.
  Outputs same dict format as before: `{id, title, text, score, num_comments, created_utc, subreddit, url}`
- `backend/tickers.py` — regex + S&P 500 CSV validation. Blacklist for common false positives.
  S&P 500 CSV auto-downloads to `backend/data/sp500_tickers.csv` on first run.
- `backend/sentiment.py` — VADER scoring. Returns compound score (-1 to +1) and bullish/bearish/neutral label.
- `backend/db.py` — MongoDB Atlas via pymongo. 3 collections: `posts`, `ticker_snapshots`, `prices`.
- `backend/prices.py` — yfinance wrapper for hourly close + volume.
- `backend/scheduler.py` — APScheduler, runs full pipeline every 30 min. Entry point: `python scheduler.py`
- `backend/requirements.txt` — all deps pinned (fastapi, uvicorn, pymongo, vaderSentiment, yfinance, etc.)

**Infrastructure:**
- MongoDB Atlas M0 free cluster: `kalereddittrader.0hiy6zq.mongodb.net`, database `sentiment_trader`
- `.env` at project root — contains only `MONGODB_URI` (not committed)

**How to populate data (run this before testing the frontend):**
```
cd backend
python -c "from scheduler import run_full_pipeline; run_full_pipeline()"
```
This takes ~30–60s. Watch for output like:
```
[scraper] Trending: NVDA, TSLA, AMD, ...
[scraper] NVDA: 30 messages
...
[pipeline] Run complete. Tickers processed: AMD, AAPL, NVDA, ...
```

### Phase 2: FastAPI Backend — COMPLETE

`backend/main.py` — 5 endpoints, CORS middleware included, verified working.

| Method | Route | Returns |
|---|---|---|
| GET | `/tickers/trending` | Top 10 tickers by mention count (last 24h) from `ticker_snapshots` |
| GET | `/tickers/{symbol}/sentiment` | Hourly sentiment scores over last 7 days |
| GET | `/tickers/{symbol}/price` | Hourly price over last 7 days |
| GET | `/tickers/{symbol}/combined` | Sentiment + price together (what the chart overlay uses) |
| GET | `/feed` | Latest 50 posts with tickers and scores |

Start with: `uvicorn main:app --reload` from `backend/` directory.
Swagger UI available at `http://localhost:8000/docs`.

**Important:** `/tickers/trending` returns empty array if no pipeline run has happened in the last 24h.
Always run the pipeline at least once before testing the frontend.

### Phase 3: React Frontend — BUILT, NEEDS END-TO-END VERIFICATION

Scaffolded with Vite. All component files written but **not yet verified working in browser** because
the pipeline was broken (Reddit 403s) during the session when they were built.

**Files:**
- `frontend/src/api.js` — fetch wrappers for all 5 API endpoints
- `frontend/src/App.jsx` — top-level layout: header with search bar, sidebar + main content area
- `frontend/src/App.css` — all styles (index.css is cleared)
- `frontend/src/components/TrendingTickers.jsx` — sidebar list, fetches `/tickers/trending`
- `frontend/src/components/TickerCard.jsx` — fetches `/combined`, renders chart + sentiment badge
- `frontend/src/components/PriceOverlay.jsx` — Recharts ComposedChart, dual Y-axis (sentiment + price)
- `frontend/src/components/SentimentChart.jsx` — standalone LineChart for sentiment only

**To start the frontend:** `npm run dev` from `frontend/` directory → `http://localhost:5173`

**What to verify:**
1. Trending tickers appear in the left sidebar (requires pipeline run first)
2. Clicking a ticker opens TickerCard with the dual-axis chart
3. Searching a ticker (e.g. NVDA) in the search bar works
4. Searching an unknown ticker shows the error state gracefully
5. No console errors

**Known issue to watch for:** The `ticker_snapshots` collection stores the `hour` field as a UTC
datetime. If the pipeline runs but the sidebar still shows empty, check that the MongoDB `hour` field
timezone matches the query (`datetime.now(timezone.utc) - timedelta(hours=24)`).

---

## Project Structure (current)
```
Reddit-Stock-Tracker/
├── backend/
│   ├── main.py               # FastAPI app — 5 endpoints
│   ├── scraper.py            # StockTwits scraper (replaced Reddit scraper)
│   ├── sentiment.py          # VADER scoring
│   ├── tickers.py            # Ticker extraction + S&P 500 validation
│   ├── prices.py             # yfinance price fetching
│   ├── db.py                 # MongoDB connection + upsert helpers
│   ├── scheduler.py          # APScheduler pipeline runner + entry point
│   ├── requirements.txt
│   └── data/
│       └── sp500_tickers.csv # auto-downloaded, gitignored
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css         # cleared — styles all in App.css
│   │   ├── main.jsx          # Vite entry point, untouched
│   │   ├── api.js
│   │   └── components/
│   │       ├── TrendingTickers.jsx
│   │       ├── TickerCard.jsx
│   │       ├── PriceOverlay.jsx
│   │       └── SentimentChart.jsx
│   ├── package.json
│   └── node_modules/         # gitignored
├── .env                      # NOT committed — MONGODB_URI only
├── .env.example
├── .gitignore
└── RedditStockHANDOFF.md
```

---

## Tech Stack
| Layer | Choice |
|---|---|
| Scraping | `requests` → StockTwits public API (no auth) |
| Sentiment | VADER (upgrade to FinBERT is Phase 4) |
| Ticker extraction | regex + S&P 500 CSV |
| Price data | yfinance |
| Backend | FastAPI + uvicorn |
| Database | MongoDB Atlas M0 (pymongo) |
| Frontend | React (Vite) + Recharts |

---

## Environment Variables (.env)
```
MONGODB_URI=mongodb+srv://...
```
No other credentials needed.

---

## Key Gotchas
1. **StockTwits rate limits** — 1s delay between requests is safe; don't remove it
2. **30 messages per symbol** — StockTwits caps each symbol stream at 30 messages. The scraper
   pulls up to 20 symbols per run, giving ~600 messages max per pipeline run. This is sufficient.
3. **VADER is not finance-tuned** — "sick gains" scores negative. Note this limitation; FinBERT is Phase 4
4. **yfinance can be flaky** — already wrapped in try/except; MongoDB upsert deduplicates
5. **MongoDB free tier** — 512MB cap, ~112MB baseline overhead. Plenty of headroom.
6. **Trending window** — `/tickers/trending` only looks back 24h. If the pipeline hasn't run
   recently, the sidebar will be empty. Always run the pipeline first.

---

## What's Left

### Immediate (do this first)
1. Run the pipeline once to populate MongoDB with fresh StockTwits data:
   ```
   cd backend
   python -c "from scheduler import run_full_pipeline; run_full_pipeline()"
   ```
2. Start both servers:
   - Backend: `uvicorn main:app --reload` from `backend/`
   - Frontend: `npm run dev` from `frontend/`
3. Open `http://localhost:5173` and verify all 5 UI checkpoints listed in Phase 3 above
4. Fix any bugs found during verification

### Phase 4: Optional Upgrades (after frontend is verified)
- **Swap VADER → FinBERT** — `ProsusAI/finbert` on HuggingFace. Finance-tuned, handles "sick gains"
  correctly. Drop-in replacement in `sentiment.py`.
- **Discord alert bot** — `bot/alert_bot.py`. Ping a channel when a ticker's mention count is 3x
  its rolling average.
- **Pearson correlation score** — compute 24h sentiment vs next-day price delta, store in a new
  `correlations` collection, expose via a new API endpoint.

---

## How to Frame This on a Resume
- Built a full-stack financial sentiment platform that aggregates StockTwits social data, extracts
  stock ticker mentions via NLP, and correlates crowd sentiment with real-time price data
- Designed a React dashboard with overlaid sentiment/price charts using Recharts, backed by a
  FastAPI REST API and MongoDB Atlas for time-series storage
- Implemented an automated data pipeline with 30-minute scheduled scraping intervals using APScheduler

---

## Next Agent Instructions
1. Load this file — it is the single source of truth
2. **Do not touch Reddit** — it is fully blocked, all three approaches failed (see top of this file)
3. The scraper is already rewritten to StockTwits in `backend/scraper.py`
4. Run the pipeline first, then start both servers, then verify the frontend end-to-end
5. Fix any frontend bugs, then move to Phase 4 if the user wants
