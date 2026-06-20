import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Equity Backtesting Platform API"


def test_health():
    r = client.get("/api/data/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("healthy", "unhealthy")
    assert "data_source" in data


def test_list_stocks():
    r = client.get("/api/stocks/")
    assert r.status_code == 200
    assert len(r.json()) >= 100


def test_run_backtest():
    payload = {
        "start_date": "2019-01-01",
        "end_date": "2023-12-31",
        "initial_capital": 1000000,
        "portfolio_size": 10,
        "rebalance_frequency": "quarterly",
        "position_sizing": "equal",
        "filters": [{"metric": "roce", "operator": ">", "value": 10}],
        "ranking_rules": [{"metric": "roe", "direction": "desc", "weight": 1}],
        "include_benchmark": True,
    }
    r = client.post("/api/backtest/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert len(data["equity_curve"]) > 0


def test_prebuilt_strategy():
    r = client.post("/api/backtest/strategies/quality_momentum/run")
    assert r.status_code == 200
    assert r.json()["success"] is True
