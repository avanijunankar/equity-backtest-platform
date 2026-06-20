"""In-memory demo dataset — no database required."""

from __future__ import annotations

from datetime import date
from functools import lru_cache

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.data_collection.stock_universe import INDIAN_STOCKS
from app.providers.base import DataProvider


class DemoDataProvider(DataProvider):
    """Generates realistic synthetic market data with a fixed seed."""

    @property
    def source_name(self) -> str:
        return "demo"

    def __init__(self) -> None:
        settings = get_settings()
        self._seed = settings.demo_data_seed
        self._prices, self._metrics, self._benchmark, self._companies = _build_demo_dataset(
            self._seed
        )

    def get_metrics_as_of(self, as_of: date) -> pd.DataFrame:
        ts = pd.Timestamp(as_of)
        eligible = self._metrics[self._metrics["as_of_date"] <= ts]
        if eligible.empty:
            return pd.DataFrame()
        idx = eligible.groupby("symbol")["as_of_date"].idxmax()
        return eligible.loc[idx].reset_index(drop=True)

    def get_prices(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        mask = (
            self._prices["symbol"].isin(symbols)
            & (self._prices["trade_date"] >= pd.Timestamp(start))
            & (self._prices["trade_date"] <= pd.Timestamp(end))
        )
        return self._prices.loc[mask].copy()

    def get_benchmark_prices(self, name: str, start: date, end: date) -> pd.DataFrame:
        mask = (self._benchmark["trade_date"] >= pd.Timestamp(start)) & (
            self._benchmark["trade_date"] <= pd.Timestamp(end)
        )
        df = self._benchmark.loc[mask].copy()
        df["benchmark_name"] = name
        return df

    def list_companies(self) -> pd.DataFrame:
        return self._companies.copy()


@lru_cache(maxsize=1)
def _build_demo_dataset(seed: int):
    rng = np.random.default_rng(seed)
    symbols = [s["symbol"] for s in INDIAN_STOCKS]
    n = len(symbols)

    companies = pd.DataFrame(
        [
            {
                "symbol": s["symbol"],
                "name": s["name"],
                "sector": rng.choice(
                    ["Financials", "IT", "Energy", "Consumer", "Healthcare", "Industrials"]
                ),
                "industry": s["name"].split()[0],
            }
            for s in INDIAN_STOCKS
        ]
    )

    # Stock-specific fundamentals (stable characteristics)
    base_caps = rng.uniform(500, 80000, n)
    base_roe = rng.uniform(8, 35, n)
    base_roce = base_roe + rng.uniform(-3, 5, n)
    base_pe = rng.uniform(8, 45, n)
    base_pb = rng.uniform(1, 8, n)
    base_de = rng.uniform(0, 2.5, n)
    base_cr = rng.uniform(0.8, 3.5, n)
    base_dy = rng.uniform(0, 4, n)
    base_rg = rng.uniform(-0.05, 0.45, n)
    base_pm = rng.uniform(2, 25, n)
    base_pat = rng.uniform(50, 15000, n)

    # Daily prices 2015-01-01 to 2024-12-31
    dates = pd.bdate_range("2015-01-01", "2024-12-31")
    price_rows: list[dict] = []

    for i, sym in enumerate(symbols):
        start_price = rng.uniform(100, 3500)
        daily_ret = rng.normal(0.0003, 0.018, len(dates))
        prices = start_price * np.cumprod(1 + daily_ret)
        for d, p in zip(dates, prices):
            price_rows.append(
                {
                    "symbol": sym,
                    "trade_date": d.date(),
                    "open": round(p * 0.998, 2),
                    "high": round(p * 1.01, 2),
                    "low": round(p * 0.99, 2),
                    "close": round(p, 2),
                    "adj_close": round(p, 2),
                    "volume": int(rng.integers(100000, 5000000)),
                }
            )

    prices_df = pd.DataFrame(price_rows)
    prices_df["trade_date"] = pd.to_datetime(prices_df["trade_date"])

    # Quarterly metrics
    metric_dates = pd.date_range("2015-03-31", "2024-12-31", freq="QE")
    metric_rows: list[dict] = []

    for i, sym in enumerate(symbols):
        sym_prices = prices_df[prices_df["symbol"] == sym].set_index("trade_date")["adj_close"]
        for md in metric_dates:
            ts = md.date()
            idx = sym_prices.index.get_indexer([md], method="ffill")[0]
            price_ratio = float(sym_prices.iloc[idx] / sym_prices.iloc[0]) if idx >= 0 else 1.0
            noise = rng.normal(0, 0.05)
            metric_rows.append(
                {
                    "symbol": sym,
                    "name": INDIAN_STOCKS[i]["name"],
                    "as_of_date": ts,
                    "market_cap_cr": round(float(base_caps[i] * price_ratio), 2),
                    "pe_ratio": round(max(5, float(base_pe[i] / max(price_ratio, 0.5) + noise * 3)), 2),
                    "pb_ratio": round(float(base_pb[i]), 2),
                    "roe": round(float(base_roe[i] + noise * 2), 2),
                    "roce": round(float(base_roce[i] + noise * 2), 2),
                    "roa": round(float(base_roe[i] * 0.6), 2),
                    "debt_to_equity": round(float(base_de[i]), 2),
                    "current_ratio": round(float(base_cr[i]), 2),
                    "dividend_yield": round(float(base_dy[i]), 2),
                    "revenue_growth": round(float(base_rg[i]), 4),
                    "pat_margin": round(float(base_pm[i]), 2),
                    "pat": round(float(base_pat[i] * price_ratio), 2),
                }
            )

    metrics_df = pd.DataFrame(metric_rows)
    metrics_df["as_of_date"] = pd.to_datetime(metrics_df["as_of_date"])

    # Nifty 50 benchmark
    bench_ret = rng.normal(0.00035, 0.012, len(dates))
    bench_prices = 8000 * np.cumprod(1 + bench_ret)
    benchmark_df = pd.DataFrame(
        {
            "trade_date": pd.to_datetime([d.date() for d in dates]),
            "close": np.round(bench_prices, 2),
            "adj_close": np.round(bench_prices, 2),
        }
    )

    return prices_df, metrics_df, benchmark_df, companies
