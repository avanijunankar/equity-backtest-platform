"""Rank stocks by single or composite metrics."""

from typing import Any

import pandas as pd


def rank_stocks(df: pd.DataFrame, ranking_rules: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Rank stocks based on ranking rules.

    Each rule: {"metric": "roe", "direction": "desc", "weight": 1.0}
    direction: 'asc' or 'desc'
    Composite ranking averages individual percentile ranks weighted by rule weight.
    """
    if df.empty or not ranking_rules:
        return df

    result = df.copy()
    rank_columns = []
    total_weight = sum(r.get("weight", 1.0) for r in ranking_rules)

    for i, rule in enumerate(ranking_rules):
        metric = rule.get("metric")
        direction = rule.get("direction", "desc")
        weight = rule.get("weight", 1.0)

        if metric not in result.columns:
            continue

        ascending = direction == "asc"
        rank_col = f"_rank_{i}"
        result[rank_col] = result[metric].rank(ascending=ascending, method="average", na_option="bottom")
        result[rank_col] = result[rank_col] * (weight / total_weight)
        rank_columns.append(rank_col)

    if rank_columns:
        result["composite_rank"] = result[rank_columns].sum(axis=1)
        result = result.sort_values("composite_rank", ascending=True)
        result = result.drop(columns=rank_columns)

    return result.reset_index(drop=True)
