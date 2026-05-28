import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(os.getenv("MONGODB_URI"))
    return _client


def get_db():
    return get_client()["sentiment_trader"]


def posts_col() -> Collection:
    return get_db()["posts"]


def snapshots_col() -> Collection:
    return get_db()["ticker_snapshots"]


def prices_col() -> Collection:
    return get_db()["prices"]


def ensure_indexes():
    posts_col().create_index([("id", ASCENDING)], unique=True)
    posts_col().create_index([("created_utc", DESCENDING)])
    posts_col().create_index([("tickers", ASCENDING)])
    snapshots_col().create_index([("ticker", ASCENDING), ("hour", DESCENDING)])
    prices_col().create_index([("ticker", ASCENDING), ("timestamp", DESCENDING)])


def upsert_post(post: dict):
    posts_col().update_one({"id": post["id"]}, {"$set": post}, upsert=True)


def upsert_price_record(record: dict):
    prices_col().update_one(
        {"ticker": record["ticker"], "timestamp": record["timestamp"]},
        {"$set": record},
        upsert=True,
    )


def upsert_snapshot(snapshot: dict):
    snapshots_col().update_one(
        {"ticker": snapshot["ticker"], "hour": snapshot["hour"]},
        {"$set": snapshot},
        upsert=True,
    )
