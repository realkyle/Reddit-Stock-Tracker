import yfinance as yf
from datetime import datetime, timezone


def get_price_history(ticker: str, period: str = "7d", interval: str = "1h") -> list[dict]:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            return []

        records = []
        for ts, row in hist.iterrows():
            records.append({
                "ticker": ticker,
                "timestamp": ts.to_pydatetime().replace(tzinfo=timezone.utc),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]),
            })
        return records
    except Exception as e:
        print(f"[prices] ERROR fetching {ticker}: {e}")
        return []


def get_current_price(ticker: str) -> float | None:
    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        return round(float(info.last_price), 4)
    except Exception as e:
        print(f"[prices] ERROR getting current price for {ticker}: {e}")
        return None
