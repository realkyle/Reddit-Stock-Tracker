import time
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.stocktwits.com/api/2"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
REQUEST_DELAY = 1.0

# Scraped on every run if trending fetch fails or to pad out symbol coverage
SEED_SYMBOLS = [
    "SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMD",
    "META", "MSFT", "AMZN", "GOOGL", "GME", "AMC",
]


def _parse_message(msg: dict) -> dict:
    created_at = msg.get("created_at", "")
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        created_utc = dt.timestamp()
    except Exception:
        created_utc = 0.0

    username = msg.get("user", {}).get("username", "unknown")
    msg_id = str(msg.get("id", ""))

    return {
        "id": f"st_{msg_id}",
        "title": msg.get("body", ""),
        "text": "",
        "score": msg.get("likes", {}).get("total", 0),
        "num_comments": msg.get("reshares", {}).get("reshared_count", 0),
        "created_utc": created_utc,
        "subreddit": "stocktwits",
        "url": f"https://stocktwits.com/{username}/message/{msg_id}",
    }


def _fetch_trending_symbols() -> list[str]:
    url = f"{BASE_URL}/streams/trending.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        symbols = resp.json().get("symbols", [])
        return [s["symbol"] for s in symbols if "symbol" in s]
    except requests.RequestException as e:
        print(f"[scraper] ERROR fetching trending symbols: {e}")
        return []


def _fetch_symbol_messages(symbol: str) -> list[dict]:
    url = f"{BASE_URL}/streams/symbol/{symbol}.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        messages = resp.json().get("messages", [])
        return [_parse_message(m) for m in messages]
    except requests.RequestException as e:
        print(f"[scraper] ERROR fetching {symbol}: {e}")
        return []


def scrape_all(limit: int = 100) -> list[dict]:
    trending = _fetch_trending_symbols()
    print(f"[scraper] Trending: {', '.join(trending) if trending else 'none — using seeds only'}")
    time.sleep(REQUEST_DELAY)

    # Merge trending + seeds, preserve order, deduplicate, cap at 20 symbols
    symbols = list(dict.fromkeys(trending + SEED_SYMBOLS))[:20]

    all_posts: list[dict] = []
    seen_ids: set[str] = set()

    for symbol in symbols:
        messages = _fetch_symbol_messages(symbol)
        new = [m for m in messages if m["id"] not in seen_ids]
        seen_ids.update(m["id"] for m in new)
        all_posts.extend(new)
        print(f"[scraper] {symbol}: {len(messages)} messages")
        time.sleep(REQUEST_DELAY)

        if len(all_posts) >= limit:
            break

    return all_posts[:limit]
