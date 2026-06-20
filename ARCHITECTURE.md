# Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                         │
│  Dashboard │ Builder │ Results │ Compare │ Data │ Settings  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST
┌──────────────────────────▼──────────────────────────────────┐
│                     FastAPI Backend                          │
│  api/routes │ schemas │ services │ backtest engine           │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │   DataProvider Factory   │
              └────────────┬────────────┘
         ┌─────────────────┼─────────────────┐
         ▼                                   ▼
  DemoDataProvider                  DatabaseDataProvider
  (in-memory, default)              (PostgreSQL via SQLAlchemy)
```

## Key Modules

| Module | Path | Role |
|--------|------|------|
| Backtest Engine | `backend/app/backtest/engine.py` | Simulation loop |
| Filters | `backend/app/backtest/filters.py` | Universe screening |
| Ranking | `backend/app/backtest/ranking.py` | Composite rank |
| Position Sizing | `backend/app/backtest/position_sizing.py` | Weight allocation |
| Metrics | `backend/app/backtest/metrics.py` | CAGR, Sharpe, etc. |
| Demo Provider | `backend/app/providers/demo.py` | No-DB data |
| DB Provider | `backend/app/providers/database.py` | PostgreSQL access |
| Data Ingestion | `backend/app/data_collection/` | Yahoo Finance |

## Design Principles

- **No look-ahead bias:** Point-in-time metrics only
- **Provider abstraction:** Swap demo ↔ database via env var
- **Service layer:** Business logic never in React components
- **Type safety:** Pydantic schemas + TypeScript interfaces
