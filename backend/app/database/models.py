"""
SQLAlchemy models — maps to PostgreSQL schema.
Primary tables: stocks, price_history, income_statements, balance_sheets,
cash_flows, fundamental_metrics, benchmark_data
"""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    yahoo_symbol: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(100))
    exchange: Mapped[str] = mapped_column(String(20), default="NSE")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    prices: Mapped[list["PriceHistory"]] = relationship(back_populates="stock")
    metrics: Mapped[list["FundamentalMetric"]] = relationship(back_populates="stock")


# Alias for backward compatibility
Company = Stock


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (UniqueConstraint("stock_id", "trade_date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[float | None] = mapped_column(Numeric(18, 4))
    high: Mapped[float | None] = mapped_column(Numeric(18, 4))
    low: Mapped[float | None] = mapped_column(Numeric(18, 4))
    close: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    adj_close: Mapped[float | None] = mapped_column(Numeric(18, 4))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    stock: Mapped["Stock"] = relationship(back_populates="prices")


StockPrice = PriceHistory


class IncomeStatement(Base):
    __tablename__ = "income_statements"
    __table_args__ = (UniqueConstraint("stock_id", "period_end", "period_type"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)
    revenue_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    pat_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    ebitda_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    eps: Mapped[float | None] = mapped_column(Numeric(18, 4))
    gross_profit_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    operating_income_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class BalanceSheet(Base):
    __tablename__ = "balance_sheets"
    __table_args__ = (UniqueConstraint("stock_id", "period_end", "period_type"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)
    total_assets_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    total_equity_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    total_debt_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    current_assets_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    current_liabilities_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    cash_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class CashFlow(Base):
    __tablename__ = "cash_flows"
    __table_args__ = (UniqueConstraint("stock_id", "period_end", "period_type"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)
    operating_cf_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    investing_cf_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    financing_cf_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    free_cash_flow_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    capex_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class FundamentalMetric(Base):
    __tablename__ = "fundamental_metrics"
    __table_args__ = (UniqueConstraint("stock_id", "as_of_date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"))
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    market_cap_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    pe_ratio: Mapped[float | None] = mapped_column(Numeric(18, 4))
    pb_ratio: Mapped[float | None] = mapped_column(Numeric(18, 4))
    roe_pct: Mapped[float | None] = mapped_column(Numeric(10, 4))
    roce_pct: Mapped[float | None] = mapped_column(Numeric(10, 4))
    roa_pct: Mapped[float | None] = mapped_column(Numeric(10, 4))
    debt_to_equity: Mapped[float | None] = mapped_column(Numeric(10, 4))
    current_ratio: Mapped[float | None] = mapped_column(Numeric(10, 4))
    dividend_yield_pct: Mapped[float | None] = mapped_column(Numeric(10, 4))
    revenue_growth_pct: Mapped[float | None] = mapped_column(Numeric(10, 4))
    pat_margin_pct: Mapped[float | None] = mapped_column(Numeric(10, 4))
    pat_cr: Mapped[float | None] = mapped_column(Numeric(18, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    stock: Mapped["Stock"] = relationship(back_populates="metrics")


FinancialMetric = FundamentalMetric


class BenchmarkData(Base):
    __tablename__ = "benchmark_data"
    __table_args__ = (UniqueConstraint("benchmark_name", "trade_date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    benchmark_name: Mapped[str] = mapped_column(String(50), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    close: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    adj_close: Mapped[float | None] = mapped_column(Numeric(18, 4))


BenchmarkPrice = BenchmarkData


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    config_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result_json: Mapped[dict | None] = mapped_column(JSONB)
    data_source: Mapped[str] = mapped_column(String(50), default="postgresql")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class DataIngestionLog(Base):
    __tablename__ = "data_ingestion_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    records_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
