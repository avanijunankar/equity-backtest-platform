"""Load price and fundamental data from PostgreSQL for backtesting."""

from datetime import date

import pandas as pd
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.database.models import (
    BenchmarkData,
    FundamentalMetric,
    IncomeStatement,
    PriceHistory,
    Stock,
)


class DataLoader:
    def __init__(self, db: Session):
        self.db = db

    def get_metrics_as_of(self, as_of: date) -> pd.DataFrame:
        subq = (
            select(
                FundamentalMetric.stock_id,
                func.max(FundamentalMetric.as_of_date).label("max_date"),
            )
            .where(FundamentalMetric.as_of_date <= as_of)
            .group_by(FundamentalMetric.stock_id)
            .subquery()
        )

        stmt = (
            select(
                Stock.symbol,
                Stock.name,
                FundamentalMetric.as_of_date,
                FundamentalMetric.market_cap_cr,
                FundamentalMetric.pe_ratio,
                FundamentalMetric.pb_ratio,
                FundamentalMetric.roe_pct.label("roe"),
                FundamentalMetric.roce_pct.label("roce"),
                FundamentalMetric.roa_pct.label("roa"),
                FundamentalMetric.debt_to_equity,
                FundamentalMetric.current_ratio,
                FundamentalMetric.dividend_yield_pct.label("dividend_yield"),
                FundamentalMetric.revenue_growth_pct.label("revenue_growth"),
                FundamentalMetric.pat_margin_pct.label("pat_margin"),
                FundamentalMetric.pat_cr.label("pat"),
            )
            .join(Stock, Stock.id == FundamentalMetric.stock_id)
            .join(
                subq,
                and_(
                    FundamentalMetric.stock_id == subq.c.stock_id,
                    FundamentalMetric.as_of_date == subq.c.max_date,
                ),
            )
            .where(Stock.is_active.is_(True))
        )

        rows = self.db.execute(stmt).mappings().all()
        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        for col in df.columns:
            if col not in ("symbol", "name", "as_of_date"):
                df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

        # Enrich PAT from income statements if missing
        if df["pat"].isna().all():
            pat_map = self._get_pat_as_of(as_of)
            if pat_map:
                df["pat"] = df["symbol"].map(pat_map)

        return df

    def _get_pat_as_of(self, as_of: date) -> dict[str, float]:
        subq = (
            select(
                IncomeStatement.stock_id,
                func.max(IncomeStatement.period_end).label("max_period"),
            )
            .where(IncomeStatement.period_end <= as_of)
            .group_by(IncomeStatement.stock_id)
            .subquery()
        )
        stmt = (
            select(Stock.symbol, IncomeStatement.pat_cr)
            .join(Stock, Stock.id == IncomeStatement.stock_id)
            .join(
                subq,
                and_(
                    IncomeStatement.stock_id == subq.c.stock_id,
                    IncomeStatement.period_end == subq.c.max_period,
                ),
            )
        )
        rows = self.db.execute(stmt).mappings().all()
        return {r["symbol"]: float(r["pat_cr"]) for r in rows if r["pat_cr"] is not None}

    def get_prices(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        stmt = (
            select(
                Stock.symbol,
                PriceHistory.trade_date,
                PriceHistory.open,
                PriceHistory.high,
                PriceHistory.low,
                PriceHistory.close,
                PriceHistory.adj_close,
                PriceHistory.volume,
            )
            .join(Stock, Stock.id == PriceHistory.stock_id)
            .where(
                Stock.symbol.in_(symbols),
                PriceHistory.trade_date >= start,
                PriceHistory.trade_date <= end,
            )
            .order_by(PriceHistory.trade_date)
        )
        rows = self.db.execute(stmt).mappings().all()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        for col in ("open", "high", "low", "close", "adj_close", "volume"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
        df["adj_close"] = df["adj_close"].fillna(df["close"])
        return df

    def get_benchmark_prices(self, name: str, start: date, end: date) -> pd.DataFrame:
        stmt = (
            select(
                BenchmarkData.trade_date,
                BenchmarkData.close,
                BenchmarkData.adj_close,
            )
            .where(
                BenchmarkData.benchmark_name == name,
                BenchmarkData.trade_date >= start,
                BenchmarkData.trade_date <= end,
            )
            .order_by(BenchmarkData.trade_date)
        )
        rows = self.db.execute(stmt).mappings().all()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        for col in ("close", "adj_close"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
        return df

    def list_companies(self) -> pd.DataFrame:
        stmt = select(Stock.symbol, Stock.name, Stock.sector, Stock.industry).where(
            Stock.is_active.is_(True)
        )
        rows = self.db.execute(stmt).mappings().all()
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def get_data_stats(self) -> dict:
        return {
            "stocks": self.db.query(Stock).filter_by(is_active=True).count(),
            "prices": self.db.query(PriceHistory).count(),
            "metrics": self.db.query(FundamentalMetric).count(),
            "income_statements": self.db.query(IncomeStatement).count(),
        }

    def get_available_metrics(self) -> list[str]:
        return [
            "market_cap_cr",
            "pe_ratio",
            "pb_ratio",
            "roe",
            "roce",
            "roa",
            "debt_to_equity",
            "current_ratio",
            "dividend_yield",
            "revenue_growth",
            "pat_margin",
            "pat",
        ]
