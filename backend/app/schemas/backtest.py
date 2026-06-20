from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class FilterRule(BaseModel):
    metric: str
    operator: Literal[">", ">=", "<", "<=", "==", "!=", "between"] = ">"
    value: float | list[float]


class RankingRule(BaseModel):
    metric: str
    direction: Literal["asc", "desc"] = "desc"
    weight: float = 1.0


class BacktestRequest(BaseModel):
    start_date: date
    end_date: date
    initial_capital: float = Field(default=1_000_000, gt=0)
    portfolio_size: int = Field(default=20, ge=1, le=100)
    rebalance_frequency: Literal["monthly", "quarterly", "semiannual", "yearly", "weekly"] = "quarterly"
    position_sizing: Literal["equal", "market_cap", "metric"] = "equal"
    sizing_metric: str | None = None
    filters: list[FilterRule] = []
    ranking_rules: list[RankingRule] = []
    include_benchmark: bool = True


class BacktestResponse(BaseModel):
    success: bool
    message: str | None = None
    data_source: str | None = None
    performance: dict[str, Any] = {}
    equity_curve: list[dict[str, Any]] = []
    drawdown: list[dict[str, Any]] = []
    rolling_returns: list[dict[str, Any]] = []
    monthly_returns: list[dict[str, Any]] = []
    benchmark_curve: list[dict[str, Any]] = []
    portfolio_logs: list[dict[str, Any]] = []
    transactions: list[dict[str, Any]] = []
    top_winners: list[dict[str, Any]] = []
    top_losers: list[dict[str, Any]] = []
    config_summary: dict[str, Any] = {}
