import time
import requests

SUBREDDITS = ["wallstreetbets", "stocks", "investing"]

HEADERS = {"User-Agent": "sentiment-trader:v1.0 (personal portfolio project)"}

# Reddit allows ~1 req/sec for unauthenticated requests; be conservative
REQUEST_DELAY = 2.0


def scrape_subreddit(subreddit_name: str, limit: int = 100) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit_name}/hot.json?limit={min(limit, 100)}"
    posts = []
    after = None

    while len(posts) < limit:
        params = {"limit": 100}
        if after:
            params["after"] = after

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[scraper] ERROR fetching {subreddit_name}: {e}")
            break

        data = response.json().get("data", {})
        children = data.get("children", [])
        if not children:
            break

        for child in children:
            p = child["data"]
            posts.append({
                "id": p["id"],
                "title": p["title"],
                "text": p.get("selftext", ""),
                "score": p["score"],
                "num_comments": p["num_comments"],
                "created_utc": p["created_utc"],
                "subreddit": subreddit_name,
                "url": p["url"],
            })

        after = data.get("after")
        if not after or len(posts) >= limit:
            break

        time.sleep(REQUEST_DELAY)

    return posts[:limit]


def scrape_all(limit: int = 100) -> list[dict]:
    all_posts = []
    for sub in SUBREDDITS:
        try:
            posts = scrape_subreddit(sub, limit=limit)
            all_posts.extend(posts)
            print(f"[scraper] {sub}: {len(posts)} posts")
            time.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f"[scraper] ERROR on {sub}: {e}")
    return all_posts
