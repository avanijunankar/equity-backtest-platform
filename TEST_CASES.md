# Test Cases — Equity Backtesting Platform

Use this document to verify the application end-to-end after setup.

**Prerequisites before testing:** PostgreSQL is running, schema applied, data ingested, backend and frontend are both started.

---

## Application Links

| What | URL |
|------|-----|
| **Main Application (UI)** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **Interactive API Docs (Swagger)** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/api/data/health |
| **List Stocks** | http://localhost:8000/api/stocks/ |
| **Prebuilt Strategies** | http://localhost:8000/api/backtest/strategies |

---

## Phase 1 — Infrastructure Tests

### TC-01: Database connection health

| Field | Value |
|-------|-------|
| **Steps** | Open http://localhost:8000/api/data/health |
| **Expected** | `{"status": "healthy", "database": "connected"}` |
| **UI check** | Top-right badge on http://localhost:3000 shows **DB: connected** (green) |

### TC-02: Backend API root

| Field | Value |
|-------|-------|
| **Steps** | Open http://localhost:8000/ |
| **Expected** | JSON with `name`, `docs`, and `health` fields |

### TC-03: Frontend loads

| Field | Value |
|-------|-------|
| **Steps** | Open http://localhost:3000 |
| **Expected** | Dashboard loads with title "Equity Backtest Platform", config form on left, empty results panel on right |

### TC-04: Stock data exists

| Field | Value |
|-------|-------|
| **Steps** | Open http://localhost:8000/api/stocks/ |
| **Expected** | JSON array with 100+ companies (symbol, name, sector) |

---

## Phase 2 — UI Backtest Tests

### TC-05: Basic backtest (equal weight, quarterly)

| Field | Value |
|-------|-------|
| **Steps** | 1. Set Start Date: `2019-01-01`, End Date: `2024-12-31` |
| | 2. Initial Capital: `1000000`, Portfolio Size: `20` |
| | 3. Rebalance: Quarterly, Position Sizing: Equal Weighted |
| | 4. Remove all filters and ranking rules (or use defaults) |
| | 5. Click **Run Backtest** |
| **Expected** | Results panel shows equity curve, drawdown chart, performance metrics (CAGR, Sharpe, Max Drawdown), portfolio logs |

### TC-06: Filter — Market cap range

| Field | Value |
|-------|-------|
| **Steps** | Add filter: `market_cap_cr` **between** `1000` and `10000` |
| | Run backtest (2019–2024, top 20, quarterly) |
| **Expected** | Backtest succeeds; `config_summary.universe_size` reflects filtered count; portfolio logs show only large/mid-cap stocks |

### TC-07: Filter — ROCE > 15%

| Field | Value |
|-------|-------|
| **Steps** | Add filter: `roce` **>** `0.15` (Yahoo returns ROE/ROCE as decimal, e.g. 0.15 = 15%) |
| | Run backtest |
| **Expected** | Backtest succeeds with smaller universe than unfiltered run |

### TC-08: Filter — PAT > 0

| Field | Value |
|-------|-------|
| **Steps** | Add filter: `pat` **>** `0` |
| | Run backtest |
| **Expected** | Backtest succeeds; only profitable companies included |

### TC-09: Combined filters (assignment spec)

| Field | Value |
|-------|-------|
| **Steps** | Filters: |
| | • `market_cap_cr` between `[1000, 10000]` |
| | • `roce` > `0.15` |
| | • `pat` > `0` |
| | Ranking: ROE desc (weight 0.5), PE asc (weight 0.5) |
| | Run backtest |
| **Expected** | Successful backtest; composite ranking applied; results show winners/losers |

### TC-10: Ranking — single metric

| Field | Value |
|-------|-------|
| **Steps** | Single ranking rule: `roe` descending, weight `1` |
| | Portfolio size: 10 |
| **Expected** | Top 10 stocks by ROE selected at each rebalance |

### TC-11: Ranking — composite (multiple metrics)

| Field | Value |
|-------|-------|
| **Steps** | Two rules: `roe` desc (0.6), `pe_ratio` asc (0.4) |
| **Expected** | Backtest completes; holdings differ from single-metric ranking |

### TC-12: Position sizing — equal weighted

| Field | Value |
|-------|-------|
| **Steps** | Position Sizing: Equal Weighted, portfolio size 5 |
| | Run backtest, check portfolio logs |
| **Expected** | Each holding weight ≈ 20% (± small rounding) |

### TC-13: Position sizing — market cap weighted

| Field | Value |
|-------|-------|
| **Steps** | Position Sizing: Market Cap Weighted |
| **Expected** | Larger-cap stocks have higher weights in portfolio logs |

### TC-14: Position sizing — metric weighted (ROCE)

| Field | Value |
|-------|-------|
| **Steps** | Position Sizing: Metric Weighted, Sizing Metric: `roce` |
| **Expected** | Weights proportional to ROCE values in portfolio logs |

### TC-15: Rebalance frequency — monthly

| Field | Value |
|-------|-------|
| **Steps** | Rebalance: Monthly, date range 2022-01-01 to 2023-12-31 |
| **Expected** | `config_summary.rebalance_count` ≈ 24 (monthly over 2 years) |

### TC-16: Rebalance frequency — yearly

| Field | Value |
|-------|-------|
| **Steps** | Rebalance: Yearly, date range 2019-01-01 to 2024-12-31 |
| **Expected** | Fewer rebalance entries in portfolio logs (~5–6) |

### TC-17: Benchmark comparison (Nifty 50)

| Field | Value |
|-------|-------|
| **Steps** | Enable "Compare with Nifty 50 benchmark", run backtest |
| **Expected** | Equity curve shows dashed Nifty 50 line; metrics include `benchmark_cagr` |

### TC-18: Export to Excel

| Field | Value |
|-------|-------|
| **Steps** | After successful backtest, click **Export Excel** |
| **Expected** | Downloads `backtest_results.xlsx` with sheets: Equity Curve, Portfolio Logs, Performance |

---

## Phase 3 — Prebuilt Strategy Tests

### TC-19: Quality Momentum strategy

| Field | Value |
|-------|-------|
| **Steps** | Click **Run** on "Quality Momentum" card |
| **Expected** | Backtest runs with ROCE > 15%, market cap filter, ROE+PE ranking; results displayed |

### TC-20: Value Investing strategy

| Field | Value |
|-------|-------|
| **Steps** | Click **Run** on "Value Investing" card |
| **Expected** | Low PE + high ROE large caps; market cap weighted portfolio |

### TC-21: Small Cap Growth strategy

| Field | Value |
|-------|-------|
| **Steps** | Click **Run** on "Small Cap Growth" card |
| **Expected** | Mid-small cap universe; metric-weighted by ROCE |

---

## Phase 4 — API Tests (via Swagger at http://localhost:8000/docs)

### TC-22: POST /api/backtest/run

| Field | Value |
|-------|-------|
| **Body** | See example in README.md |
| **Expected** | `200 OK`, `success: true`, non-empty `equity_curve` and `performance` |

### TC-23: GET /api/backtest/strategies

| Field | Value |
|-------|-------|
| **Expected** | Array of 3 strategies: `quality_momentum`, `value_investing`, `small_cap_growth` |

### TC-24: POST /api/backtest/strategies/quality_momentum/run

| Field | Value |
|-------|-------|
| **Expected** | Full backtest result for prebuilt strategy |

### TC-25: POST /api/backtest/compare

| Field | Value |
|-------|-------|
| **Body** | Array of 2 backtest configs (different ranking rules) |
| **Expected** | `comparisons` array with 2 entries, each with `performance` and `equity_curve` |

### TC-26: POST /api/backtest/export

| Field | Value |
|-------|-------|
| **Body** | Result JSON from a prior backtest run |
| **Expected** | Excel file download |

---

## Phase 5 — Edge Cases & Negative Tests

### TC-27: Empty filter result

| Field | Value |
|-------|-------|
| **Steps** | Filter: `market_cap_cr` > `999999999` |
| **Expected** | Error message: "No stocks passed the filter criteria at start date" |

### TC-28: Invalid date range

| Field | Value |
|-------|-------|
| **Steps** | Start Date: `2024-01-01`, End Date: `2019-01-01` |
| **Expected** | Empty or failed result (no rebalance dates / no data) |

### TC-29: Portfolio size = 1

| Field | Value |
|-------|-------|
| **Steps** | Portfolio Size: `1` |
| **Expected** | Single stock per rebalance; weight 100% |

### TC-30: Portfolio size = 50

| Field | Value |
|-------|-------|
| **Steps** | Portfolio Size: `50` with broad filters |
| **Expected** | Up to 50 stocks if universe allows |

### TC-31: DB disconnected

| Field | Value |
|-------|-------|
| **Steps** | Stop PostgreSQL or use wrong `DATABASE_URL`, reload UI |
| **Expected** | Badge shows **DB: disconnected/error**; backtest fails with connection error |

### TC-32: No data ingested

| Field | Value |
|-------|-------|
| **Steps** | Fresh DB with schema only (no ingest) |
| **Expected** | Health OK but backtest returns "No fundamental data available for start date" |

---

## Phase 6 — Performance Metrics Validation

After any successful backtest (TC-05), verify these fields exist and are reasonable:

| Metric | Sanity Check |
|--------|--------------|
| `total_return` | Percentage, can be positive or negative |
| `cagr` | Typically -50% to +50% for 5-year Indian equity |
| `sharpe_ratio` | Usually between -1 and 3 |
| `max_drawdown` | Negative percentage (e.g. -15 to -40) |
| `volatility` | Positive percentage |
| `final_value` | Should equal last point on equity curve |
| `benchmark_cagr` | Present when benchmark enabled |

---

## Quick Smoke Test (5 minutes)

Run these in order for a fast verification:

1. ✅ http://localhost:8000/api/data/health → connected
2. ✅ http://localhost:3000 → UI loads, green DB badge
3. ✅ Run default backtest → equity curve appears
4. ✅ Run "Quality Momentum" prebuilt → results appear
5. ✅ Export Excel → file downloads

---

## Video Demo Script (for submission)

1. Show application link: http://localhost:3000
2. Show DB connected status
3. Run TC-09 (combined filters from assignment)
4. Explain equity curve + Nifty 50 benchmark overlay
5. Show drawdown chart and CAGR/Sharpe metrics
6. Show top winners/losers and portfolio logs
7. Export Excel
8. Run one prebuilt strategy
9. Optionally show Swagger at http://localhost:8000/docs
