"""
Core backtest engine with no look-ahead bias.
Uses DataProvider abstraction — works with demo or PostgreSQL data.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from app.backtest.filters import apply_filters
from app.backtest.metrics import (
    compute_drawdown_series,
    compute_monthly_returns,
    compute_performance_metrics,
    compute_rolling_returns,
)
from app.backtest.position_sizing import compute_weights
from app.backtest.ranking import rank_stocks
from app.providers.base import DataProvider


REBALANCE_FREQ_MAP = {
    "monthly": "ME",
    "quarterly": "QE",
    "semiannual": "6ME",
    "yearly": "YE",
    "weekly": "W",
}


class BacktestEngine:
    def __init__(self, provider: DataProvider):
        self.provider = provider

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        start_date = pd.Timestamp(config["start_date"])
        end_date = pd.Timestamp(config["end_date"])
        initial_capital = float(config.get("initial_capital", 1_000_000))
        portfolio_size = int(config.get("portfolio_size", 20))
        rebalance_freq = config.get("rebalance_frequency", "quarterly")
        position_sizing = config.get("position_sizing", "equal")
        sizing_metric = config.get("sizing_metric")
        filters = config.get("filters", [])
        ranking_rules = config.get("ranking_rules", [])
        include_benchmark = config.get("include_benchmark", True)

        universe_metrics = self.provider.get_metrics_as_of(start_date.date())
        if universe_metrics.empty:
            return self._empty_result("No fundamental data available for start date.")

        filtered_universe = apply_filters(universe_metrics, filters)
        if filtered_universe.empty:
            return self._empty_result("No stocks passed the filter criteria at start date.")

        eligible_symbols = filtered_universe["symbol"].tolist()
        prices = self.provider.get_prices(eligible_symbols, start_date.date(), end_date.date())
        if prices.empty:
            return self._empty_result("No price data available for filtered universe.")

        rebal_dates = self._get_rebalance_dates(start_date, end_date, rebalance_freq)
        if not rebal_dates:
            return self._empty_result("No rebalance dates in the selected range.")

        portfolio_value = initial_capital
        holdings: dict[str, float] = {}
        equity_records: list[dict] = []
        portfolio_logs: list[dict] = []
        transactions: list[dict] = []

        all_dates = sorted(prices["trade_date"].unique())
        price_pivot = prices.pivot(index="trade_date", columns="symbol", values="adj_close")
        price_pivot.index = pd.to_datetime(price_pivot.index)
        price_pivot = price_pivot.ffill()

        rebal_set = set(rebal_dates)

        for i, current_date in enumerate(all_dates):
            ts = pd.Timestamp(current_date)

            if ts in rebal_set or i == 0:
                metrics = self.provider.get_metrics_as_of(
                    current_date.date() if hasattr(current_date, "date") else current_date
                )
                metrics = metrics[metrics["symbol"].isin(eligible_symbols)]

                if not metrics.empty:
                    ranked = rank_stocks(metrics, ranking_rules)
                    selected = ranked.head(portfolio_size)["symbol"].tolist()

                    if selected:
                        weights = compute_weights(metrics, selected, position_sizing, sizing_metric)
                        exec_prices = self._get_execution_prices(price_pivot, current_date, selected)
                        valid = [s for s in selected if s in exec_prices and exec_prices[s] > 0]

                        if valid:
                            total_w = sum(weights.get(s, 0) for s in valid)
                            if total_w > 0:
                                norm_weights = {s: weights.get(s, 0) / total_w for s in valid}
                                new_holdings = {
                                    s: (portfolio_value * norm_weights[s]) / exec_prices[s]
                                    for s in valid
                                }

                                for sym, shares in new_holdings.items():
                                    transactions.append(
                                        {
                                            "date": str(current_date)[:10],
                                            "symbol": sym,
                                            "action": "BUY",
                                            "shares": round(shares, 4),
                                            "price": round(exec_prices[sym], 2),
                                            "weight_pct": round(norm_weights[sym] * 100, 2),
                                        }
                                    )

                                holdings = new_holdings
                                portfolio_logs.append(
                                    {
                                        "date": str(current_date)[:10],
                                        "portfolio_value": round(portfolio_value, 2),
                                        "holdings": [
                                            {
                                                "symbol": s,
                                                "weight": round(norm_weights[s] * 100, 2),
                                                "price": round(exec_prices[s], 2),
                                                "shares": round(holdings[s], 4),
                                            }
                                            for s in valid
                                        ],
                                    }
                                )

            if holdings:
                mtm = 0.0
                day_prices = self._get_execution_prices(
                    price_pivot, current_date, list(holdings.keys())
                )
                for sym, shares in holdings.items():
                    if sym in day_prices:
                        mtm += shares * day_prices[sym]
                portfolio_value = mtm if mtm > 0 else portfolio_value

            equity_records.append(
                {"date": current_date, "portfolio_value": round(portfolio_value, 2)}
            )

        equity_df = pd.DataFrame(equity_records)
        equity_df["date"] = pd.to_datetime(equity_df["date"])
        equity_df = equity_df.set_index("date")

        winners, losers = self._compute_winners_losers(portfolio_logs, price_pivot)
        drawdown = compute_drawdown_series(equity_df["portfolio_value"])
        rolling = compute_rolling_returns(equity_df["portfolio_value"])
        monthly = compute_monthly_returns(equity_df["portfolio_value"])

        benchmark_df = None
        if include_benchmark:
            benchmark_df = self._load_benchmark(start_date.date(), end_date.date(), initial_capital)

        perf = compute_performance_metrics(equity_df, benchmark_df)

        return {
            "success": True,
            "data_source": self.provider.source_name,
            "performance": perf,
            "equity_curve": [
                {"date": str(idx.date()), "value": row["portfolio_value"]}
                for idx, row in equity_df.iterrows()
            ],
            "drawdown": [
                {"date": str(idx.date()), "value": round(float(val) * 100, 2)}
                for idx, val in drawdown.items()
            ],
            "rolling_returns": rolling,
            "monthly_returns": monthly,
            "benchmark_curve": (
                [
                    {"date": str(idx.date()), "value": row["portfolio_value"]}
                    for idx, row in benchmark_df.iterrows()
                ]
                if benchmark_df is not None
                else []
            ),
            "portfolio_logs": portfolio_logs,
            "transactions": transactions,
            "top_winners": winners[:10],
            "top_losers": losers[:10],
            "config_summary": {
                "start_date": str(start_date.date()),
                "end_date": str(end_date.date()),
                "portfolio_size": portfolio_size,
                "rebalance_frequency": rebalance_freq,
                "position_sizing": position_sizing,
                "universe_size": len(eligible_symbols),
                "rebalance_count": len(portfolio_logs),
                "data_source": self.provider.source_name,
            },
        }

    def _get_rebalance_dates(self, start: pd.Timestamp, end: pd.Timestamp, freq: str) -> list:
        pandas_freq = REBALANCE_FREQ_MAP.get(freq, "QE")
        return list(pd.date_range(start=start, end=end, freq=pandas_freq))

    def _get_execution_prices(
        self, price_pivot: pd.DataFrame, as_of, symbols: list[str]
    ) -> dict[str, float]:
        ts = pd.Timestamp(as_of)
        if ts not in price_pivot.index:
            available = price_pivot.index[price_pivot.index <= ts]
            if available.empty:
                return {}
            ts = available[-1]
        row = price_pivot.loc[ts]
        return {s: float(row[s]) for s in symbols if s in row.index and pd.notna(row[s])}

    def _compute_winners_losers(self, logs, price_pivot):
        stock_returns: dict[str, list[float]] = {}
        for i, log in enumerate(logs):
            rebal_date = pd.Timestamp(log["date"])
            next_date = (
                pd.Timestamp(logs[i + 1]["date"]) if i + 1 < len(logs) else price_pivot.index[-1]
            )
            for holding in log["holdings"]:
                sym = holding["symbol"]
                entry_price = holding["price"]
                future = price_pivot.index[
                    (price_pivot.index >= rebal_date) & (price_pivot.index <= next_date)
                ]
                if len(future) > 1 and sym in price_pivot.columns:
                    exit_price = float(price_pivot.loc[future[-1], sym])
                    if entry_price > 0:
                        stock_returns.setdefault(sym, []).append((exit_price / entry_price) - 1)

        aggregated = [
            {"symbol": sym, "avg_return": round(float(np.mean(rets)) * 100, 2), "periods": len(rets)}
            for sym, rets in stock_returns.items()
        ]
        aggregated.sort(key=lambda x: x["avg_return"], reverse=True)
        return aggregated[:10], sorted(aggregated, key=lambda x: x["avg_return"])[:10]

    def _load_benchmark(self, start: date, end: date, initial_capital: float):
        bench = self.provider.get_benchmark_prices("NIFTY50", start, end)
        if bench.empty:
            return None
        bench = bench.sort_values("trade_date")
        first_price = float(bench.iloc[0]["adj_close"] or bench.iloc[0]["close"])
        bench["portfolio_value"] = initial_capital * (
            bench["adj_close"].fillna(bench["close"]) / first_price
        )
        bench["date"] = pd.to_datetime(bench["trade_date"])
        return bench.set_index("date")[["portfolio_value"]]

    def _empty_result(self, message: str) -> dict[str, Any]:
        return {
            "success": False,
            "message": message,
            "data_source": self.provider.source_name,
            "performance": {},
            "equity_curve": [],
            "drawdown": [],
            "rolling_returns": [],
            "monthly_returns": [],
            "benchmark_curve": [],
            "portfolio_logs": [],
            "transactions": [],
            "top_winners": [],
            "top_losers": [],
        }
