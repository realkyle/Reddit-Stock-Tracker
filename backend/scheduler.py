import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from apscheduler.schedulers.background import BackgroundScheduler

from scraper import scrape_all
from tickers import extract_tickers
from sentiment import score_post
from db import ensure_indexes, upsert_post, upsert_price_record, upsert_snapshot
from prices import get_price_history


def run_full_pipeline():
    print(f"\n[pipeline] Starting run at {datetime.now(timezone.utc).isoformat()}")

    # Step 1: Scrape Reddit
    posts = scrape_all(limit=100)
    print(f"[pipeline] Scraped {len(posts)} posts total")

    # Step 2: Enrich each post with tickers + sentiment, then store
    ticker_posts: dict[str, list[dict]] = defaultdict(list)

    for post in posts:
        combined_text = f"{post['title']} {post['text']}"
        post["tickers"] = extract_tickers(combined_text)
        post["sentiment_score"] = score_post(post)
        upsert_post(post)

        for ticker in post["tickers"]:
            ticker_posts[ticker].append(post)

    print(f"[pipeline] Found {len(ticker_posts)} unique tickers")

    # Step 3: Aggregate hourly snapshots per ticker
    current_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    for ticker, t_posts in ticker_posts.items():
        scores = [p["sentiment_score"] for p in t_posts]
        snapshot = {
            "ticker": ticker,
            "hour": current_hour,
            "mention_count": len(t_posts),
            "avg_sentiment": round(sum(scores) / len(scores), 4),
            "post_ids": [p["id"] for p in t_posts],
        }
        upsert_snapshot(snapshot)

    # Step 4: Fetch price data for active tickers (skip if already fetched recently)
    active_tickers = list(ticker_posts.keys())
    print(f"[pipeline] Fetching prices for {len(active_tickers)} tickers")
    for ticker in active_tickers:
        records = get_price_history(ticker, period="7d", interval="1h")
        for record in records:
            upsert_price_record(record)

    print(f"[pipeline] Run complete. Tickers processed: {', '.join(sorted(active_tickers))}")


def start_scheduler(interval_minutes: int = 30):
    ensure_indexes()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_full_pipeline, "interval", minutes=interval_minutes)
    scheduler.start()
    print(f"[scheduler] Started — running every {interval_minutes} minutes")

    # Run once immediately on startup
    run_full_pipeline()

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[scheduler] Stopped")


if __name__ == "__main__":
    start_scheduler(interval_minutes=30)
