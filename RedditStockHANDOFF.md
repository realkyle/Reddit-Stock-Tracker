# HANDOFF: Reddit Sentiment Stock Tracker

## What This Project Is
A full-stack web app that scrapes Reddit financial communities (r/wallstreetbets, r/stocks, r/investing),
performs NLP sentiment analysis on posts/comments, extracts stock ticker mentions, correlates sentiment
with real price data, and visualizes trends on a dashboard. The goal is a resume project showcasing:
NLP, data pipelines, full-stack dev, and real financial data — similar structure to ValReader.

---

## What Has Been Done So Far
**Nothing has been built yet.** This HANDOFF was created at the planning/architecture stage.
No code has been written, no APIs have been tested, no environment has been set up.

---

## Agreed Architecture

### Tech Stack
| Layer | Choice | Reason |
|---|---|---|
| Scraping | `PRAW` (Python Reddit API Wrapper) | Official Reddit API, simple auth, well-documented |
| Sentiment | `VADER` first, upgrade to `FinBERT` later | VADER is fast/easy; FinBERT is finance-tuned for better accuracy |
| Ticker extraction | `regex` + optional `spaCy` | Match $TICKER patterns, filter against known ticker list |
| Price data | `yfinance` (Yahoo Finance) | Free, no API key needed, easy Python library |
| Backend | `FastAPI` (Python) | Lightweight, async-friendly, easy REST endpoints |
| Database | `MongoDB` (via `pymongo` or `motor`) | Matches user's existing experience from ValReader |
| Frontend | `React` + `Recharts` | Matches user's existing experience; Recharts for stock/sentiment charts |
| Alerting (optional) | `discord.py` bot | Pings a Discord channel when ticker mention volume spikes |

---

## Project Structure
```
sentiment-trader/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── scraper.py            # PRAW Reddit scraper
│   ├── sentiment.py          # VADER / FinBERT sentiment scoring
│   ├── tickers.py            # Ticker extraction logic
│   ├── prices.py             # yfinance price fetching
│   ├── db.py                 # MongoDB connection + queries
│   ├── scheduler.py          # APScheduler for periodic scraping
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── TickerCard.jsx       # Per-ticker sentiment + price card
│   │   │   ├── SentimentChart.jsx   # Recharts line chart: sentiment over time
│   │   │   ├── PriceOverlay.jsx     # Overlay price data on sentiment chart
│   │   │   ├── TrendingTickers.jsx  # Top mentioned tickers right now
│   │   │   └── HeatMap.jsx          # Optional: sentiment heatmap by time of day
│   │   └── api.js                   # Axios calls to FastAPI backend
│   └── package.json
├── bot/
│   └── alert_bot.py          # Optional Discord bot for spike alerts
└── README.md
```

---

## Step-by-Step Build Order

### Phase 1: Data Pipeline (Build First)
1. **Set up Reddit API credentials**
   - Go to https://www.reddit.com/prefs/apps
   - Create a "script" app, get `client_id`, `client_secret`
   - Store in `.env` file, never commit to GitHub

2. **Build scraper.py with PRAW**
```python
import praw, os
from dotenv import load_dotenv
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="sentiment-trader by u/YOUR_USERNAME"
)

def scrape_subreddit(subreddit_name="wallstreetbets", limit=100):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.hot(limit=limit):
        posts.append({
            "id": post.id,
            "title": post.title,
            "text": post.selftext,
            "score": post.score,
            "created_utc": post.created_utc,
            "subreddit": subreddit_name
        })
    return posts
```

3. **Build tickers.py — extract ticker mentions**
```python
import re

# Download full ticker list from: https://github.com/datasets/s-and-p-500-companies
# Load into a set for O(1) lookup
KNOWN_TICKERS = {"AAPL", "TSLA", "GME", "AMC", ...}  # load from CSV

def extract_tickers(text):
    # Match $TICKER pattern OR bare known tickers
    raw = re.findall(r'\$([A-Z]{1,5})', text.upper())
    return [t for t in raw if t in KNOWN_TICKERS]
```

4. **Build sentiment.py — score each post**
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def score_text(text):
    scores = analyzer.polarity_scores(text)
    return scores["compound"]  # -1.0 (very negative) to +1.0 (very positive)
```

5. **Build db.py — store results in MongoDB**
   - Collection: `posts` — raw scraped data + tickers + sentiment score
   - Collection: `ticker_snapshots` — aggregated daily sentiment per ticker
   - Collection: `prices` — price history per ticker

6. **Build prices.py — fetch price data**
```python
import yfinance as yf

def get_price_history(ticker, period="7d", interval="1h"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    return hist[["Close"]].reset_index().to_dict(orient="records")
```

7. **Build scheduler.py — run scraper every 30 mins**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(run_full_pipeline, "interval", minutes=30)
scheduler.start()
```

---

### Phase 2: FastAPI Backend
Key endpoints to build in `main.py`:

| Method | Route | Returns |
|---|---|---|
| GET | `/tickers/trending` | Top 10 tickers by mention count (last 24h) |
| GET | `/tickers/{symbol}/sentiment` | Sentiment scores over time for one ticker |
| GET | `/tickers/{symbol}/price` | Price history for one ticker |
| GET | `/tickers/{symbol}/combined` | Sentiment + price in one response for chart overlay |
| GET | `/feed` | Latest 50 scraped posts with tickers + scores |

---

### Phase 3: React Frontend
Build in this order:
1. `TrendingTickers.jsx` — simple ranked list of hottest tickers, fetch from `/tickers/trending`
2. `SentimentChart.jsx` — Recharts `<LineChart>` of sentiment score over time
3. `PriceOverlay.jsx` — second Y-axis on same chart showing price, fetch from `/combined`
4. `TickerCard.jsx` — wrap charts into a card with current sentiment label (Bullish/Bearish/Neutral)
5. `App.jsx` — search bar to look up any ticker + trending feed

---

### Phase 4: Optional Upgrades (for resume polish)
- **Swap VADER → FinBERT** for finance-specific accuracy
  - Model: `ProsusAI/finbert` on HuggingFace
  - `from transformers import pipeline; nlp = pipeline("sentiment-analysis", model="ProsusAI/finbert")`
- **Discord alert bot** — `discord.py`, ping when a ticker's 1-hour mention count is 3x its average
- **Correlation score** — simple Pearson correlation between 24h sentiment trend and next-day price delta, displayed on TickerCard

---

## Key Gotchas / Things to Watch Out For

1. **Reddit API rate limits** — PRAW handles this automatically but don't hammer it; 30-min intervals are safe
2. **Ticker false positives** — words like "IT", "NOW", "ARE" are valid tickers but not stock mentions. Always cross-reference against a known ticker CSV list, not just regex
3. **VADER is not finance-tuned** — "sick gains" scores negative with VADER. FinBERT fixes this but needs more setup. Start with VADER, note the limitation in your README
4. **yfinance can be flaky** — wrap calls in try/except; Yahoo sometimes blocks repeated requests. Add caching in MongoDB so you don't re-fetch prices you already have
5. **MongoDB free tier** — use MongoDB Atlas free tier (512MB) which is plenty for this project
6. **CORS** — add `fastapi.middleware.cors` to your FastAPI app or the React frontend won't be able to call it

---

## Environment Variables Needed (.env)
```
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USERNAME=your_reddit_username
MONGODB_URI=mongodb+srv://...
```

---

## How to Frame This on a Resume
**Bullet structure to aim for:**
- Built a full-stack sentiment analysis platform that scrapes Reddit financial communities using PRAW, extracts stock ticker mentions via NLP, and correlates crowd sentiment with real-time price data via the Yahoo Finance API
- Designed a React dashboard with overlaid sentiment/price charts using Recharts, backed by a FastAPI REST API and MongoDB for time-series storage
- Implemented automated data pipeline with 30-minute scheduled scraping intervals and optional Discord alerting on unusual ticker mention spikes

---

## Next Agent Instructions
1. Load this file — it is the single source of truth
2. Start with Phase 1 (scraper + sentiment + db) — get data flowing before touching frontend
3. Test the pipeline end-to-end with just `r/wallstreetbets` and 3 tickers (TSLA, AAPL, GME) before scaling
4. Build Phase 2 (FastAPI) next, test all endpoints with Postman or curl
5. Build Phase 3 (React) last — the frontend is the easiest part once data is solid
6. Do NOT start with the frontend — data pipeline first, always
