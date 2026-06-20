# Database Setup — Step by Step

Follow these steps **after** the application code is in place.

---

## Option A: Docker PostgreSQL (Recommended for Local Dev)

### Step 1 — Start the database

```bash
cd /path/to/trial
docker compose up -d
```

- Container name: `equity_backtest_db`
- Host: `localhost`
- Port: **5433** (mapped from container 5432)
- User: `backtest_user`
- Password: `backtest_pass`
- Database: `equity_backtest`

Verify:

```bash
docker compose exec postgres pg_isready -U backtest_user -d equity_backtest
```

### Step 2 — Configure backend

Edit `backend/.env`:

```env
USE_DATABASE=true
DATABASE_URL=postgresql://backtest_user:backtest_pass@localhost:5433/equity_backtest
```

### Step 3 — Create tables

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.init_db
```

### Step 4 — Ingest real Yahoo Finance data

```bash
python -m scripts.ingest_data --all
```

| Phase | What it does | Time |
|-------|--------------|------|
| `--seed` | 110+ NSE stock symbols | ~1 sec |
| `--prices` | OHLCV from 2015 | ~15 min |
| `--fundamentals` | P&L, balance sheet, cash flow, ratios | ~15 min |
| `--benchmarks` | Nifty 50 index | ~1 min |

Monitor progress:

```bash
tail -f ../ingest.log
```

### Step 5 — Verify data in PostgreSQL

```bash
docker compose exec postgres psql -U backtest_user -d equity_backtest -c "SELECT COUNT(*) FROM stocks;"
docker compose exec postgres psql -U backtest_user -d equity_backtest -c "SELECT COUNT(*) FROM price_history;"
docker compose exec postgres psql -U backtest_user -d equity_backtest -c "SELECT COUNT(*) FROM fundamental_metrics;"
```

Expected: 110+ stocks, thousands of price rows, hundreds of metric rows.

### Step 6 — Start application

```bash
# Backend
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm run dev
```

Open http://localhost:3000 — badge should show **PostgreSQL**, not Demo.

---

## Option B: Cloud PostgreSQL (Neon / Supabase — Browser Only)

### Step 1 — Create database (Chrome)

1. Go to https://neon.tech (or https://supabase.com)
2. Sign up → Create project → Copy **connection string**

### Step 2 — Configure backend

```env
USE_DATABASE=true
DATABASE_URL=postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require
```

### Step 3–6 — Same as Option A

Run `init_db`, `ingest_data --all`, start servers.

---

## Database Schema (Tables)

| Table | Purpose |
|-------|---------|
| `stocks` | Master list of NSE companies |
| `price_history` | Daily OHLCV |
| `income_statements` | P&L (revenue, PAT, EBITDA) |
| `balance_sheets` | Assets, equity, debt |
| `cash_flows` | Operating/investing/financing CF |
| `fundamental_metrics` | ROE, ROCE, PE, market cap (point-in-time) |
| `benchmark_data` | Nifty 50 prices |
| `backtest_runs` | Saved backtest results (optional) |
| `data_ingestion_log` | Audit trail |

Indexes on `(stock_id, trade_date)` and `(stock_id, as_of_date)` for fast screening.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5432 in use | Use port 5433 in docker-compose (already configured) |
| `connection refused` | Run `docker compose up -d` |
| Empty backtest / demo fallback | Run `ingest_data --all` |
| Yahoo rate limits | Re-run ingestion; 0.4s delay built in |
| Docker mount error | Schema applied via `init_db.py` instead |

---

## Stop / Reset Database

```bash
docker compose down      # stop
docker compose down -v   # stop + delete all data
```
