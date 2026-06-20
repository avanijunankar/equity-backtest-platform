"""Filter stocks based on fundamental criteria at a point in time."""

from typing import Any

import pandas as pd


def apply_filters(df: pd.DataFrame, filters: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Apply user-defined filters to a metrics DataFrame.

    Each filter: {"metric": "roce", "operator": ">", "value": 15}
    Supported operators: >, >=, <, <=, ==, !=, between
    """
    if df.empty or not filters:
        return df

    result = df.copy()

    for f in filters:
        metric = f.get("metric")
        operator = f.get("operator", ">")
        value = f.get("value")

        if metric not in result.columns:
            continue

        col = pd.to_numeric(result[metric], errors="coerce")

        if operator == ">":
            result = result[col > value]
        elif operator == ">=":
            result = result[col >= value]
        elif operator == "<":
            result = result[col < value]
        elif operator == "<=":
            result = result[col <= value]
        elif operator == "==":
            result = result[col == value]
        elif operator == "!=":
            result = result[col != value]
        elif operator == "between":
            low, high = value if isinstance(value, (list, tuple)) else (0, value)
            result = result[(col >= low) & (col <= high)]

    return result.reset_index(drop=True)
