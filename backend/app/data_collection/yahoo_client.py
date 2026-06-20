"""Yahoo Finance HTTP client with browser User-Agent (required by Yahoo API)."""

import logging
import time
from datetime import datetime

import pandas as pd
import requests
import yfinance as yf

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def get_ticker(symbol: str) -> yf.Ticker:
    return yf.Ticker(symbol, session=_session)


def fetch_history(symbol: str, start: str = "2015-01-01", end: str | None = None) -> pd.DataFrame:
    """Fetch OHLCV via yfinance with retries, fallback to chart API."""
    for attempt in range(3):
        try:
            ticker = get_ticker(symbol)
            hist = ticker.history(start=start, end=end, auto_adjust=True)
            if not hist.empty:
                return hist
        except Exception as exc:
            logger.warning("yfinance attempt %d for %s: %s", attempt + 1, symbol, exc)
        time.sleep(1 + attempt)

    return _fetch_chart_api(symbol, start, end)


def _fetch_chart_api(symbol: str, start: str, end: str | None) -> pd.DataFrame:
    period1 = int(datetime.strptime(start, "%Y-%m-%d").timestamp())
    period2 = int(datetime.now().timestamp()) if not end else int(
        datetime.strptime(end, "%Y-%m-%d").timestamp()
    )
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?interval=1d&period1={period1}&period2={period2}"
    )
    resp = _session.get(url, timeout=30)
    if resp.status_code == 429:
        logger.warning("Yahoo rate limit for %s, waiting 15s...", symbol)
        time.sleep(15)
        resp = _session.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    result = data.get("chart", {}).get("result", [])
    if not result:
        return pd.DataFrame()

    q = result[0]
    ts = q.get("timestamp") or []
    quotes = q.get("indicators", {}).get("quote", [{}])[0]
    if not ts:
        return pd.DataFrame()

    df = pd.DataFrame(
        {
            "Open": quotes.get("open"),
            "High": quotes.get("high"),
            "Low": quotes.get("low"),
            "Close": quotes.get("close"),
            "Volume": quotes.get("volume"),
        },
        index=pd.to_datetime(ts, unit="s"),
    )
    return df.dropna(subset=["Close"])


def fetch_info(symbol: str) -> dict:
    for attempt in range(3):
        try:
            info = get_ticker(symbol).info
            if info:
                return info
        except Exception as exc:
            logger.warning("info attempt %d for %s: %s", attempt + 1, symbol, exc)
        time.sleep(1 + attempt)
    return {}
