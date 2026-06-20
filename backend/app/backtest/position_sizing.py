"""Position sizing methods for portfolio construction."""

from typing import Any

import numpy as np
import pandas as pd


def equal_weight(symbols: list[str]) -> dict[str, float]:
    if not symbols:
        return {}
    weight = 1.0 / len(symbols)
    return {s: weight for s in symbols}


def market_cap_weight(df: pd.DataFrame, symbols: list[str]) -> dict[str, float]:
    subset = df[df["symbol"].isin(symbols)].copy()
    if subset.empty:
        return equal_weight(symbols)

    caps = subset.set_index("symbol")["market_cap_cr"].fillna(0)
    total = caps.sum()
    if total <= 0:
        return equal_weight(symbols)

    return {s: float(caps.get(s, 0) / total) for s in symbols}


def metric_weight(df: pd.DataFrame, symbols: list[str], metric: str) -> dict[str, float]:
    subset = df[df["symbol"].isin(symbols)].copy()
    if subset.empty:
        return equal_weight(symbols)

    values = subset.set_index("symbol")[metric].fillna(0).clip(lower=0)
    total = values.sum()
    if total <= 0:
        return equal_weight(symbols)

    return {s: float(values.get(s, 0) / total) for s in symbols}


def compute_weights(
    df: pd.DataFrame,
    symbols: list[str],
    method: str,
    metric: str | None = None,
) -> dict[str, float]:
    method = method.lower()
    if method == "equal":
        return equal_weight(symbols)
    if method == "market_cap":
        return market_cap_weight(df, symbols)
    if method == "metric" and metric:
        return metric_weight(df, symbols, metric)
    return equal_weight(symbols)
