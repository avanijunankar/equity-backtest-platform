"""Performance analytics for backtest results."""

import math
from typing import Any

import numpy as np
import pandas as pd


def compute_cagr(equity_curve: pd.Series) -> float:
    if len(equity_curve) < 2:
        return 0.0
    start_val = equity_curve.iloc[0]
    end_val = equity_curve.iloc[-1]
    if start_val <= 0:
        return 0.0
    years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
    if years <= 0:
        return 0.0
    return float((end_val / start_val) ** (1 / years) - 1)


def compute_sharpe(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    if returns.empty or returns.std() == 0:
        return 0.0
    daily_rf = (1 + risk_free_rate) ** (1 / 252) - 1
    excess = returns - daily_rf
    return float(np.sqrt(252) * excess.mean() / excess.std())


def compute_max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    return float(drawdown.min())


def compute_sortino(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    if returns.empty:
        return 0.0
    daily_rf = (1 + risk_free_rate) ** (1 / 252) - 1
    excess = returns - daily_rf
    downside = excess[excess < 0]
    if downside.empty or downside.std() == 0:
        return 0.0
    return float(np.sqrt(252) * excess.mean() / downside.std())


def compute_calmar(cagr: float, max_dd: float) -> float:
    if max_dd == 0:
        return 0.0
    return float(cagr / abs(max_dd))


def compute_volatility(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(252))


def compute_performance_metrics(
    equity_curve: pd.DataFrame,
    benchmark_curve: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Compute full performance analytics from equity curve DataFrame."""
    if equity_curve.empty:
        return {}

    portfolio = equity_curve["portfolio_value"].copy()
    returns = portfolio.pct_change().dropna()

    cagr = compute_cagr(portfolio)
    max_dd = compute_max_drawdown(portfolio)
    sharpe = compute_sharpe(returns)
    sortino = compute_sortino(returns)
    volatility = compute_volatility(returns)
    calmar = compute_calmar(cagr, max_dd)
    total_return = float(portfolio.iloc[-1] / portfolio.iloc[0] - 1) if portfolio.iloc[0] > 0 else 0.0

    metrics: dict[str, Any] = {
        "total_return": round(total_return * 100, 2),
        "cagr": round(cagr * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "sortino_ratio": round(sortino, 3),
        "max_drawdown": round(max_dd * 100, 2),
        "calmar_ratio": round(calmar, 3),
        "volatility": round(volatility * 100, 2),
        "final_value": round(float(portfolio.iloc[-1]), 2),
        "initial_value": round(float(portfolio.iloc[0]), 2),
    }

    if benchmark_curve is not None and not benchmark_curve.empty:
        bench = benchmark_curve["portfolio_value"].reindex(portfolio.index, method="ffill")
        bench_returns = bench.pct_change().dropna()
        bench_cagr = compute_cagr(bench)
        metrics["benchmark_cagr"] = round(bench_cagr * 100, 2)
        metrics["benchmark_total_return"] = round(
            float(bench.iloc[-1] / bench.iloc[0] - 1) * 100, 2
        ) if bench.iloc[0] > 0 else 0.0

        aligned_returns = returns.reindex(bench_returns.index).dropna()
        aligned_bench = bench_returns.reindex(aligned_returns.index).dropna()
        if len(aligned_returns) > 1 and aligned_bench.std() > 0:
            cov = np.cov(aligned_returns, aligned_bench)[0, 1]
            beta = cov / aligned_bench.var()
            metrics["beta"] = round(float(beta), 3)
            metrics["alpha"] = round(float(cagr - (0.06 + beta * (bench_cagr - 0.06))) * 100, 2)

    return metrics


def compute_drawdown_series(equity_curve: pd.Series) -> pd.Series:
    rolling_max = equity_curve.cummax()
    return (equity_curve - rolling_max) / rolling_max


def compute_rolling_returns(equity_curve: pd.Series, window: int = 252) -> list[dict]:
    if len(equity_curve) < window:
        return []
    rolling = equity_curve.pct_change(window).dropna()
    return [
        {"date": str(idx.date()), "value": round(float(val) * 100, 2)}
        for idx, val in rolling.items()
    ]


def compute_monthly_returns(equity_curve: pd.Series) -> list[dict]:
    monthly = equity_curve.resample("ME").last().pct_change().dropna()
    return [
        {"month": str(idx.date())[:7], "return": round(float(val) * 100, 2)}
        for idx, val in monthly.items()
    ]
