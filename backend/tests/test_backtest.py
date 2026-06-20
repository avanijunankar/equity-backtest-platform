import pytest
import pandas as pd

from app.backtest.filters import apply_filters
from app.backtest.ranking import rank_stocks
from app.backtest.position_sizing import equal_weight, compute_weights
from app.backtest.metrics import compute_cagr, compute_sharpe, compute_max_drawdown


@pytest.fixture
def sample_metrics():
    return pd.DataFrame([
        {"symbol": "A", "roce": 20, "roe": 18, "pe_ratio": 15, "market_cap_cr": 5000, "pat": 100},
        {"symbol": "B", "roce": 10, "roe": 12, "pe_ratio": 25, "market_cap_cr": 2000, "pat": 50},
        {"symbol": "C", "roce": 25, "roe": 22, "pe_ratio": 12, "market_cap_cr": 10000, "pat": 200},
    ])


def test_filter_roce(sample_metrics):
    result = apply_filters(sample_metrics, [{"metric": "roce", "operator": ">", "value": 15}])
    assert len(result) == 2
    assert set(result["symbol"]) == {"A", "C"}


def test_filter_between(sample_metrics):
    result = apply_filters(sample_metrics, [{"metric": "market_cap_cr", "operator": "between", "value": [3000, 8000]}])
    assert len(result) == 1
    assert result.iloc[0]["symbol"] == "A"


def test_composite_ranking(sample_metrics):
    rules = [
        {"metric": "roe", "direction": "desc", "weight": 0.5},
        {"metric": "pe_ratio", "direction": "asc", "weight": 0.5},
    ]
    ranked = rank_stocks(sample_metrics, rules)
    assert ranked.iloc[0]["symbol"] == "C"


def test_equal_weight():
    w = equal_weight(["A", "B", "C", "D"])
    assert sum(w.values()) == pytest.approx(1.0)
    assert w["A"] == 0.25


def test_market_cap_weight(sample_metrics):
    w = compute_weights(sample_metrics, ["A", "C"], "market_cap")
    assert w["C"] > w["A"]


def test_cagr():
    s = pd.Series([100, 110, 121], index=pd.date_range("2020-01-01", periods=3, freq="YE"))
    assert compute_cagr(s) > 0


def test_sharpe():
    returns = pd.Series([0.01, -0.005, 0.02, 0.015, -0.01])
    assert isinstance(compute_sharpe(returns), float)


def test_max_drawdown():
    s = pd.Series([100, 120, 90, 110])
    assert compute_max_drawdown(s) < 0
