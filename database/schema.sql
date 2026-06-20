-- Equity Backtesting Platform - PostgreSQL Schema (Requirements-compliant)
-- Auto-applied by Docker on first start, or run manually on cloud PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- stocks (master)
CREATE TABLE IF NOT EXISTS stocks (
    id              SERIAL PRIMARY KEY,
    symbol          VARCHAR(20) NOT NULL UNIQUE,
    yahoo_symbol    VARCHAR(30) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    sector          VARCHAR(100),
    industry        VARCHAR(100),
    exchange        VARCHAR(20) DEFAULT 'NSE',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);

-- Legacy alias: companies view points to stocks
CREATE OR REPLACE VIEW companies AS SELECT * FROM stocks;

-- price_history (OHLCV)
CREATE TABLE IF NOT EXISTS price_history (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    trade_date      DATE NOT NULL,
    open            NUMERIC(18, 4),
    high            NUMERIC(18, 4),
    low             NUMERIC(18, 4),
    close           NUMERIC(18, 4) NOT NULL,
    adj_close       NUMERIC(18, 4),
    volume          BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stock_id, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_price_history_stock_date ON price_history(stock_id, trade_date);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(trade_date);

-- P&L / Income statements
CREATE TABLE IF NOT EXISTS income_statements (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    period_end      DATE NOT NULL,
    period_type     VARCHAR(10) NOT NULL CHECK (period_type IN ('quarterly', 'annual')),
    revenue_cr      NUMERIC(18, 4),
    pat_cr          NUMERIC(18, 4),
    ebitda_cr       NUMERIC(18, 4),
    eps             NUMERIC(18, 4),
    gross_profit_cr NUMERIC(18, 4),
    operating_income_cr NUMERIC(18, 4),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stock_id, period_end, period_type)
);

CREATE INDEX IF NOT EXISTS idx_income_stock_period ON income_statements(stock_id, period_end DESC);

-- Balance sheets
CREATE TABLE IF NOT EXISTS balance_sheets (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    period_end      DATE NOT NULL,
    period_type     VARCHAR(10) NOT NULL CHECK (period_type IN ('quarterly', 'annual')),
    total_assets_cr NUMERIC(18, 4),
    total_equity_cr NUMERIC(18, 4),
    total_debt_cr   NUMERIC(18, 4),
    current_assets_cr NUMERIC(18, 4),
    current_liabilities_cr NUMERIC(18, 4),
    cash_cr         NUMERIC(18, 4),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stock_id, period_end, period_type)
);

CREATE INDEX IF NOT EXISTS idx_balance_stock_period ON balance_sheets(stock_id, period_end DESC);

-- Cash flow statements
CREATE TABLE IF NOT EXISTS cash_flows (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    period_end      DATE NOT NULL,
    period_type     VARCHAR(10) NOT NULL CHECK (period_type IN ('quarterly', 'annual')),
    operating_cf_cr NUMERIC(18, 4),
    investing_cf_cr NUMERIC(18, 4),
    financing_cf_cr NUMERIC(18, 4),
    free_cash_flow_cr NUMERIC(18, 4),
    capex_cr        NUMERIC(18, 4),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stock_id, period_end, period_type)
);

CREATE INDEX IF NOT EXISTS idx_cashflow_stock_period ON cash_flows(stock_id, period_end DESC);

-- fundamental_metrics (ratios & valuation — point-in-time)
CREATE TABLE IF NOT EXISTS fundamental_metrics (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    as_of_date      DATE NOT NULL,
    market_cap_cr   NUMERIC(18, 4),
    pe_ratio        NUMERIC(18, 4),
    pb_ratio        NUMERIC(18, 4),
    roe_pct         NUMERIC(10, 4),
    roce_pct        NUMERIC(10, 4),
    roa_pct         NUMERIC(10, 4),
    debt_to_equity  NUMERIC(10, 4),
    current_ratio   NUMERIC(10, 4),
    dividend_yield_pct NUMERIC(10, 4),
    revenue_growth_pct NUMERIC(10, 4),
    pat_margin_pct  NUMERIC(10, 4),
    pat_cr          NUMERIC(18, 4),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stock_id, as_of_date)
);

CREATE INDEX IF NOT EXISTS idx_fundamental_stock_date ON fundamental_metrics(stock_id, as_of_date DESC);
CREATE INDEX IF NOT EXISTS idx_fundamental_market_cap ON fundamental_metrics(market_cap_cr);
CREATE INDEX IF NOT EXISTS idx_fundamental_roce ON fundamental_metrics(roce_pct);

-- benchmark_data (Nifty 50)
CREATE TABLE IF NOT EXISTS benchmark_data (
    id              BIGSERIAL PRIMARY KEY,
    benchmark_name  VARCHAR(50) NOT NULL,
    trade_date      DATE NOT NULL,
    close           NUMERIC(18, 4) NOT NULL,
    adj_close       NUMERIC(18, 4),
    UNIQUE (benchmark_name, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_benchmark_data_date ON benchmark_data(benchmark_name, trade_date);

-- backtest_runs (persistence)
CREATE TABLE IF NOT EXISTS backtest_runs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255),
    config_json     JSONB NOT NULL,
    result_json     JSONB,
    data_source     VARCHAR(50) DEFAULT 'postgresql',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- portfolio_holdings per rebalance
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id              BIGSERIAL PRIMARY KEY,
    backtest_run_id UUID REFERENCES backtest_runs(id) ON DELETE CASCADE,
    rebalance_date  DATE NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    weight_pct      NUMERIC(10, 4),
    shares          NUMERIC(18, 4),
    price           NUMERIC(18, 4),
    portfolio_value NUMERIC(18, 4)
);

CREATE INDEX IF NOT EXISTS idx_holdings_run ON portfolio_holdings(backtest_run_id);

-- portfolio_transactions
CREATE TABLE IF NOT EXISTS portfolio_transactions (
    id              BIGSERIAL PRIMARY KEY,
    backtest_run_id UUID REFERENCES backtest_runs(id) ON DELETE CASCADE,
    trade_date      DATE NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    action          VARCHAR(10) NOT NULL,
    shares          NUMERIC(18, 4),
    price           NUMERIC(18, 4),
    weight_pct      NUMERIC(10, 4)
);

-- data ingestion audit
CREATE TABLE IF NOT EXISTS data_ingestion_log (
    id              BIGSERIAL PRIMARY KEY,
    source          VARCHAR(50) NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,
    records_count   INTEGER DEFAULT 0,
    status          VARCHAR(20) NOT NULL,
    message         TEXT,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

-- Compatibility views for existing ORM (maps old names)
CREATE OR REPLACE VIEW stock_prices AS
    SELECT id, stock_id AS company_id, trade_date, open, high, low, close, adj_close, volume, created_at
    FROM price_history;

CREATE OR REPLACE VIEW financial_metrics AS
    SELECT id, stock_id AS company_id, as_of_date,
           market_cap_cr, pe_ratio, pb_ratio,
           roe_pct AS roe, roce_pct AS roce, roa_pct AS roa,
           debt_to_equity, current_ratio,
           dividend_yield_pct AS dividend_yield,
           revenue_growth_pct AS revenue_growth,
           pat_margin_pct AS pat_margin,
           pat_cr AS pat, created_at
    FROM fundamental_metrics;

CREATE OR REPLACE VIEW benchmark_prices AS
    SELECT id, benchmark_name, trade_date, close, adj_close FROM benchmark_data;

CREATE OR REPLACE VIEW financial_statements AS
    SELECT i.id, i.stock_id AS company_id, i.period_end, i.period_type,
           NULL::INTEGER AS fiscal_year, NULL::INTEGER AS fiscal_quarter,
           i.revenue_cr AS revenue, i.pat_cr AS pat, i.ebitda_cr AS ebitda, i.eps,
           b.total_assets_cr AS total_assets, b.total_equity_cr AS total_equity,
           b.total_debt_cr AS total_debt,
           c.operating_cf_cr AS operating_cash_flow, c.free_cash_flow_cr AS free_cash_flow,
           i.created_at, i.created_at AS updated_at
    FROM income_statements i
    LEFT JOIN balance_sheets b ON b.stock_id = i.stock_id AND b.period_end = i.period_end AND b.period_type = i.period_type
    LEFT JOIN cash_flows c ON c.stock_id = i.stock_id AND c.period_end = i.period_end AND c.period_type = i.period_type;
