# Documentation — Equity Backtesting Platform

## 1. Project Overview

This platform lets users define fundamental equity strategies (filters + ranking + position sizing), backtest them on historical Indian stock data, and visualize performance with benchmark comparison against Nifty 50.

## 2. Directory Structure

```
trial/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Environment settings (DATABASE_URL, CORS)
│   │   ├── api/routes/
│   │   │   ├── backtest.py         # Backtest, export, compare endpoints
│   │   │   ├── stocks.py           # Stock listing, available metrics
│   │   │   └── data.py             # Health check, data ingestion triggers
│   │   ├── backtest/
│   │   │   ├── engine.py           # Core simulation loop
│   │   │   ├── filters.py          # Universe filtering
│   │   │   ├── ranking.py          # Single & composite ranking
│   │   │   ├── position_sizing.py  # Equal, market cap, metric weights
│   │   │   └── metrics.py          # CAGR, Sharpe, drawdown, etc.
│   │   ├── data_collection/
│   │   │   ├── stock_universe.py   # 110+ NSE stock list
│   │   │   └── yahoo_finance.py    # Price & fundamental fetcher
│   │   ├── database/
│   │   │   ├── connection.py       # SQLAlchemy engine & session
│   │   │   └── models.py           # ORM models
│   │   ├── schemas/
│   │   │   └── backtest.py         # Pydantic request/response models
│   │   └── services/
│   │       ├── data_loader.py      # DB queries for backtest
│   │       └── prebuilt_strategies.py
│   ├── scripts/
│   │   └── ingest_data.py          # CLI data ingestion
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/                    # Next.js App Router
│       ├── components/
│       │   ├── Dashboard.tsx       # Main layout & orchestration
│       │   ├── BacktestConfig.tsx  # Parameter form
│       │   └── BacktestResults.tsx # Charts & tables
│       └── lib/
│           └── api.ts              # Backend API client
├── database/
│   └── schema.sql                  # PostgreSQL DDL
├── README.md
└── DOCUMENTATION.md
```

## 3. Module Descriptions

### 3.1 Backtest Engine (`backend/app/backtest/engine.py`)

The engine runs a event-driven simulation:

1. **Initial filter** (once at `start_date`): Applies user filters to the fundamental universe. Only stocks passing filters remain eligible for the entire backtest.
2. **Rebalance loop**: On each rebalance date (monthly/quarterly/yearly), fetches point-in-time metrics (latest data ≤ rebalance date).
3. **Ranking**: Sorts eligible stocks using composite rank (weighted average of individual metric ranks).
4. **Selection**: Takes top N stocks (`portfolio_size`).
5. **Position sizing**: Assigns weights via equal, market cap, or metric-weighted methods.
6. **Execution**: Buys at rebalance-date prices (or last available price before that date).
7. **Daily MTM**: Marks portfolio to market using adjusted close prices.
8. **Compounding**: Full portfolio value is reinvested at each rebalance.

**No look-ahead bias**: Metrics use `as_of_date <= rebalance_date`. Prices use `trade_date <= execution_date`.

### 3.2 Filters (`backend/app/backtest/filters.py`)

Supported operators: `>`, `>=`, `<`, `<=`, `==`, `!=`, `between`.

Example filters:
- Market cap between ₹1000 Cr and ₹10000 Cr
- ROCE > 15%
- PAT > 0 (via `pat` metric from financial statements)

### 3.3 Ranking (`backend/app/backtest/ranking.py`)

Each rule assigns a rank to stocks for a metric. Composite rank = weighted sum of individual ranks (lower is better).

Example: 50% ROE descending + 50% PE ascending.

### 3.4 Position Sizing (`backend/app/backtest/position_sizing.py`)

| Method | Description |
|--------|-------------|
| `equal` | 1/N weight for each holding |
| `market_cap` | Weight proportional to market cap |
| `metric` | Weight proportional to a chosen metric (e.g., ROCE) |

### 3.5 Performance Metrics (`backend/app/backtest/metrics.py`)

| Metric | Formula / Description |
|--------|----------------------|
| CAGR | (End/Start)^(1/years) - 1 |
| Sharpe | sqrt(252) × mean(excess return) / std |
| Sortino | Like Sharpe but downside deviation only |
| Max Drawdown | Min of (value - peak) / peak |
| Calmar | CAGR / |Max DD| |
| Beta/Alpha | vs Nifty 50 benchmark |

### 3.6 Data Collection (`backend/app/data_collection/yahoo_finance.py`)

- **Source**: Yahoo Finance via `yfinance` library
- **Symbols**: NSE stocks use `.NS` suffix (e.g., `RELIANCE.NS`)
- **Prices**: Daily OHLCV from 2015 onwards
- **Fundamentals**: P&L, balance sheet, cash flow from quarterly statements
- **Metrics**: PE, PB, ROE, ROCE, market cap, etc.
- **Historical metrics**: Quarterly snapshots derived from price ratios for backtesting
- **Benchmark**: Nifty 50 (`^NSEI`)

### 3.7 Database Schema (`database/schema.sql`)

| Table | Purpose |
|-------|---------|
| `companies` | Stock master (symbol, name, sector) |
| `stock_prices` | Daily OHLCV |
| `financial_statements` | P&L, balance sheet, cash flow |
| `financial_metrics` | Ratios & valuation metrics |
| `benchmark_prices` | Nifty 50 index prices |
| `data_ingestion_log` | Audit trail for data fetches |

Indexes on `(company_id, trade_date)`, `(company_id, as_of_date)`, and filter columns.

## 4. Frontend Components

### Dashboard
- DB health indicator
- Prebuilt strategy cards
- Two-column layout: config (left) + results (right)

### BacktestConfig
- Date range, capital, portfolio size, rebalance frequency
- Dynamic filter and ranking rule builders
- Position sizing selector

### BacktestResults
- Performance metric cards
- Equity curve with benchmark overlay (Recharts)
- Drawdown area chart
- Top winners/losers tables
- Portfolio rebalance logs

## 5. Assumptions

1. **Currency**: All values in INR; market cap stored in Crores (Cr).
2. **Execution**: Trades execute at close price on rebalance date (no slippage/commissions modeled).
3. **ROCE**: When not available from Yahoo, approximated from ROE.
4. **Historical fundamentals**: Quarterly metric snapshots use current fundamentals scaled by price ratio — suitable for demonstration; production systems should use actual historical filings.
5. **Universe filter**: Applied once at start date per assignment spec; stocks leaving/entering filter criteria mid-backtest are not re-evaluated.
6. **Delisted stocks**: Not explicitly handled; price data gaps forward-filled.
7. **Risk-free rate**: 6% for Sharpe/Sortino calculations (India approximate).

## 6. Optional Features Implemented

- ✅ FastAPI REST endpoints
- ✅ Prebuilt strategies (Quality Momentum, Value Investing, Small Cap Growth)
- ✅ Strategy comparison endpoint (`POST /api/backtest/compare`)
- ✅ Nifty 50 benchmark comparison
- ✅ Excel export

## 7. Remote Database Integration Steps

Since the database runs on a separate device:

### On DB Device:
1. Install PostgreSQL 14+
2. Create `equity_backtest` database and user
3. Run `database/schema.sql`
4. Configure `listen_addresses` and `pg_hba.conf` for remote access
5. Run data ingestion:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # DATABASE_URL=postgresql://...@localhost:5432/equity_backtest
   python -m scripts.ingest_data --all
   ```

### On App Device (this TRIAL folder):
1. Set `backend/.env`:
   ```
   DATABASE_URL=postgresql://backtest_user:password@DB_DEVICE_IP:5432/equity_backtest
   ```
2. Start backend: `uvicorn app.main:app --reload`
3. Start frontend: `npm run dev`
4. Verify green "DB: connected" badge in UI

### Network Checklist:
- [ ] DB device IP reachable: `ping DB_DEVICE_IP`
- [ ] Port open: `nc -zv DB_DEVICE_IP 5432`
- [ ] Correct credentials in DATABASE_URL
- [ ] Data ingested (companies + prices + metrics exist)

## 8. Future Enhancements

- Historical fundamental data from Screener.in scraping
- Transaction costs and slippage modeling
- Walk-forward optimization
- User authentication and saved strategies
- Real-time data refresh scheduler
