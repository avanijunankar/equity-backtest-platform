# API Reference

Base URL: `http://localhost:8000`

## Backtest

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/backtest/run` | Run custom backtest |
| GET | `/api/backtest/strategies` | List prebuilt strategies |
| POST | `/api/backtest/strategies/{id}/run` | Run prebuilt strategy |
| POST | `/api/backtest/compare` | Compare 2-5 strategies |
| POST | `/api/backtest/export` | Export Excel |
| GET | `/api/backtest/history` | Backtest history (DB mode) |
| GET | `/api/backtest/{id}` | Get run by ID (DB mode) |

## Stocks & Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stocks/` | List companies |
| GET | `/api/stocks/metrics` | Available filter metrics |
| GET | `/api/data/health` | Health + data source |
| POST | `/api/data/sync` | Sync Yahoo Finance (DB mode) |

## Example Request

```json
POST /api/backtest/run
{
  "start_date": "2018-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 1000000,
  "portfolio_size": 20,
  "rebalance_frequency": "quarterly",
  "position_sizing": "equal",
  "filters": [
    {"metric": "roce", "operator": ">", "value": 15},
    {"metric": "market_cap_cr", "operator": "between", "value": [1000, 50000]}
  ],
  "ranking_rules": [
    {"metric": "roe", "direction": "desc", "weight": 0.5},
    {"metric": "pe_ratio", "direction": "asc", "weight": 0.5}
  ],
  "include_benchmark": true
}
```

Interactive docs: http://localhost:8000/docs
