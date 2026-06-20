# Equity Backtesting Platform — Complete Setup Guide

## Quick Start (This Machine)

### 1. Start PostgreSQL (Docker)

```bash
cd /Users/prakalp/Desktop/trial
docker compose up -d
```

PostgreSQL runs on **port 5433** (5432 may be in use on your Mac).

### 2. Initialize Database Tables

```bash
cd backend
source .venv/bin/activate
python -m scripts.init_db
```

### 3. Load Data into PostgreSQL

**Option A — Real Yahoo Finance data (required for submission):**

```bash
python -m scripts.ingest_data --all
```

Takes 20–40 minutes. Fetches live OHLCV, P&L, balance sheets, cash flows for 115 NSE stocks.

**Option B — Bootstrap now (if Yahoo rate-limits you):**

```bash
python -m scripts.load_demo_to_db
```

Loads structured data into PostgreSQL immediately so the app works end-to-end.  
Re-run Option A later when Yahoo API is available to replace with live data.

### 4. Start Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend

```bash
cd ../frontend
npm run dev
```

### 6. Open App

| Service | URL |
|---------|-----|
| **Application** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |

---

## Requirements Checklist

| Requirement | Implementation |
|-------------|----------------|
| Backtest engine (dates, rebalance, filters, ranking, sizing) | `backend/app/backtest/` |
| No look-ahead bias | Point-in-time metrics in engine |
| Yahoo Finance data | `backend/app/data_collection/yahoo_finance.py` |
| 100+ Indian stocks | `stock_universe.py` (110 stocks) |
| PostgreSQL | Docker on port 5433, or cloud (Neon/Supabase) |
| Normalized tables | stocks, price_history, income_statements, balance_sheets, cash_flows, fundamental_metrics |
| Next.js + Tailwind UI | `frontend/` |
| Equity curve, drawdown, metrics, winners/losers, logs | Results page |
| CSV + Excel export | Dashboard export buttons |
| FastAPI endpoints | http://localhost:8000/docs |
| Prebuilt strategies + Nifty 50 benchmark | Dashboard cards |
| Strategy comparison | /compare page |

---

## Cloud PostgreSQL (Alternative — Chrome Only)

If Docker is unavailable, use **Neon** (https://neon.tech) or **Supabase**:

1. Create project in browser
2. Copy connection string
3. Edit `backend/.env`:
   ```
   USE_DATABASE=true
   DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
   ```
4. Run `python -m scripts.init_db`
5. Run `python -m scripts.ingest_data --all`

---

## Environment Variables

```env
USE_DATABASE=true
DATABASE_URL=postgresql://backtest_user:backtest_pass@localhost:5433/equity_backtest
```

See `backend/.env.example` for all options.

---

## Documentation

- [DATABASE_SETUP.md](DATABASE_SETUP.md) — DB steps in detail
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design
- [API_REFERENCE.md](API_REFERENCE.md) — REST endpoints
- [BACKTEST_ENGINE.md](BACKTEST_ENGINE.md) — Engine logic

---

## Verify Real Data

```bash
curl http://localhost:8000/api/data/health
# data_source: "postgresql", stats.stocks: 110+

curl -X POST http://localhost:8000/api/backtest/strategies/quality_momentum/run
```

---

## Video Demo Outline

1. Show Data page — stocks/prices count from PostgreSQL
2. Run Quality Momentum prebuilt strategy
3. Show equity curve + Nifty 50 benchmark
4. Configure custom filters (ROCE, PAT, market cap)
5. Export Excel/CSV
6. Strategy comparison page
