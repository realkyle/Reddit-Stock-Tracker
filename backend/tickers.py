import re
import os
import pandas as pd
import requests

TICKER_CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "sp500_tickers.csv")

# Words that are valid tickers but are never stock mentions in financial text
TICKER_BLACKLIST = {
    "A", "I", "IT", "BE", "GO", "ON", "AT", "IN", "IS", "BY", "OR", "IF",
    "DO", "ME", "MY", "US", "AN", "AM", "AS", "NO", "OK", "SO", "TO", "UP",
    "ARE", "FOR", "HAS", "HIM", "HIS", "HOW", "ITS", "MAY", "NEW", "NOT",
    "NOW", "OLD", "ONE", "OUR", "OUT", "OWN", "RIG", "SAY", "SHE", "THE",
    "TWO", "WAS", "WHO", "WHY", "ALL", "ANY", "AND", "BUT", "CAN", "DID",
    "GET", "GOT", "HAD", "HIM", "HIT", "LET", "MAN", "PUT", "RAN", "RUN",
    "SAW", "SET", "SIT", "TEN", "TOO", "USE", "WAY", "WIN", "YES", "YET",
}

_ticker_set: set[str] | None = None


def _download_ticker_list() -> set[str]:
    os.makedirs(os.path.dirname(TICKER_CSV_PATH), exist_ok=True)
    url = (
        "https://raw.githubusercontent.com/datasets/s-and-p-500-companies"
        "/main/data/constituents.csv"
    )
    try:
        df = pd.read_csv(url)
        df.to_csv(TICKER_CSV_PATH, index=False)
        print(f"[tickers] Downloaded {len(df)} S&P 500 tickers")
        return set(df["Symbol"].str.upper().tolist())
    except Exception as e:
        print(f"[tickers] Download failed: {e}. Using fallback list.")
        return {"AAPL", "TSLA", "GME", "AMC", "MSFT", "GOOGL", "AMZN", "META",
                "NVDA", "NFLX", "AMD", "INTC", "BABA", "SPY", "QQQ", "BAC",
                "JPM", "WMT", "DIS", "PYPL", "SNAP", "TWTR", "UBER", "LYFT"}


def load_tickers() -> set[str]:
    global _ticker_set
    if _ticker_set is not None:
        return _ticker_set

    if os.path.exists(TICKER_CSV_PATH):
        df = pd.read_csv(TICKER_CSV_PATH)
        _ticker_set = set(df["Symbol"].str.upper().tolist())
        print(f"[tickers] Loaded {len(_ticker_set)} tickers from cache")
    else:
        _ticker_set = _download_ticker_list()

    _ticker_set -= TICKER_BLACKLIST
    return _ticker_set


def extract_tickers(text: str) -> list[str]:
    if not text:
        return []

    known = load_tickers()

    # Match explicit $TICKER mentions
    dollar_mentions = re.findall(r"\$([A-Z]{1,5})", text.upper())

    # Match bare uppercase words that are known tickers (2+ chars to reduce noise)
    bare_mentions = re.findall(r"\b([A-Z]{2,5})\b", text.upper())

    candidates = set(dollar_mentions) | {t for t in bare_mentions if t in known}
    return sorted(candidates & known)
