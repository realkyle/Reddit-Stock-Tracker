from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING, DESCENDING

from db import posts_col, snapshots_col, prices_col
from sentiment import label

app = FastAPI(title="Reddit Sentiment Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/tickers/trending")
def trending_tickers():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    pipeline = [
        {"$match": {"hour": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$ticker",
            "mention_count": {"$sum": "$mention_count"},
            "avg_sentiment": {"$avg": "$avg_sentiment"},
        }},
        {"$sort": {"mention_count": -1}},
        {"$limit": 10},
    ]
    results = list(snapshots_col().aggregate(pipeline))
    return [
        {
            "ticker": r["_id"],
            "mention_count": r["mention_count"],
            "avg_sentiment": round(r["avg_sentiment"], 4),
            "sentiment_label": label(r["avg_sentiment"]),
        }
        for r in results
    ]


@app.get("/tickers/{symbol}/sentiment")
def ticker_sentiment(symbol: str):
    symbol = symbol.upper()
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    docs = list(
        snapshots_col()
        .find(
            {"ticker": symbol, "hour": {"$gte": cutoff}},
            {"_id": 0, "hour": 1, "avg_sentiment": 1, "mention_count": 1},
        )
        .sort("hour", ASCENDING)
    )
    if not docs:
        raise HTTPException(status_code=404, detail=f"No sentiment data for {symbol}")
    return [
        {
            "time": d["hour"].isoformat(),
            "avg_sentiment": d["avg_sentiment"],
            "mention_count": d["mention_count"],
            "sentiment_label": label(d["avg_sentiment"]),
        }
        for d in docs
    ]


@app.get("/tickers/{symbol}/price")
def ticker_price(symbol: str):
    symbol = symbol.upper()
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    docs = list(
        prices_col()
        .find(
            {"ticker": symbol, "timestamp": {"$gte": cutoff}},
            {"_id": 0, "timestamp": 1, "close": 1, "volume": 1},
        )
        .sort("timestamp", ASCENDING)
    )
    if not docs:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol}")
    return [
        {
            "time": d["timestamp"].isoformat(),
            "close": d["close"],
            "volume": d["volume"],
        }
        for d in docs
    ]


@app.get("/tickers/{symbol}/combined")
def ticker_combined(symbol: str):
    symbol = symbol.upper()
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    sentiment_docs = list(
        snapshots_col()
        .find(
            {"ticker": symbol, "hour": {"$gte": cutoff}},
            {"_id": 0, "hour": 1, "avg_sentiment": 1, "mention_count": 1},
        )
        .sort("hour", ASCENDING)
    )
    price_docs = list(
        prices_col()
        .find(
            {"ticker": symbol, "timestamp": {"$gte": cutoff}},
            {"_id": 0, "timestamp": 1, "close": 1, "volume": 1},
        )
        .sort("timestamp", ASCENDING)
    )

    if not sentiment_docs and not price_docs:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")

    return {
        "ticker": symbol,
        "sentiment": [
            {
                "time": d["hour"].isoformat(),
                "avg_sentiment": d["avg_sentiment"],
                "mention_count": d["mention_count"],
                "sentiment_label": label(d["avg_sentiment"]),
            }
            for d in sentiment_docs
        ],
        "price": [
            {
                "time": d["timestamp"].isoformat(),
                "close": d["close"],
                "volume": d["volume"],
            }
            for d in price_docs
        ],
    }


@app.get("/feed")
def feed():
    docs = list(
        posts_col()
        .find(
            {"tickers": {"$exists": True, "$ne": []}},
            {
                "_id": 0,
                "id": 1,
                "title": 1,
                "subreddit": 1,
                "url": 1,
                "score": 1,
                "num_comments": 1,
                "tickers": 1,
                "sentiment_score": 1,
                "created_utc": 1,
            },
        )
        .sort("created_utc", DESCENDING)
        .limit(50)
    )
    return [
        {
            "id": d["id"],
            "title": d["title"],
            "subreddit": d["subreddit"],
            "url": d["url"],
            "score": d["score"],
            "num_comments": d["num_comments"],
            "tickers": d.get("tickers", []),
            "sentiment_score": d.get("sentiment_score", 0.0),
            "sentiment_label": label(d.get("sentiment_score", 0.0)),
            "created_utc": d["created_utc"],
        }
        for d in docs
    ]
