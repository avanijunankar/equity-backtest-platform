"""Populate PostgreSQL from demo dataset when Yahoo Finance is rate-limited.

Run: python -m scripts.load_demo_to_db
Use ingest_data --all when Yahoo API is available for real market data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data_collection.stock_universe import INDIAN_STOCKS
from app.database.connection import SessionLocal, engine, Base
from app.database.models import BenchmarkData, FundamentalMetric, PriceHistory, Stock
from app.providers.demo import _build_demo_dataset


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    prices, metrics, benchmark, companies = _build_demo_dataset(42)

    print("Loading stocks...")
    symbol_to_id = {}
    for s in INDIAN_STOCKS:
        row = db.query(Stock).filter_by(symbol=s["symbol"]).first()
        if not row:
            row = Stock(
                symbol=s["symbol"],
                yahoo_symbol=s["yahoo_symbol"],
                name=s["name"],
                exchange="NSE",
            )
            db.add(row)
            db.flush()
        symbol_to_id[s["symbol"]] = row.id
    db.commit()

    print("Loading price history...")
    batch = []
    for _, r in prices.iterrows():
        sid = symbol_to_id.get(r["symbol"])
        if not sid:
            continue
        td = r["trade_date"].date() if hasattr(r["trade_date"], "date") else r["trade_date"]
        if db.query(PriceHistory).filter_by(stock_id=sid, trade_date=td).first():
            continue
        batch.append(
            PriceHistory(
                stock_id=sid,
                trade_date=td,
                open=r["open"],
                high=r["high"],
                low=r["low"],
                close=r["close"],
                adj_close=r["adj_close"],
                volume=r["volume"],
            )
        )
        if len(batch) >= 5000:
            db.add_all(batch)
            db.commit()
            batch = []
    if batch:
        db.add_all(batch)
        db.commit()

    print("Loading fundamental metrics...")
    batch = []
    for _, r in metrics.iterrows():
        sid = symbol_to_id.get(r["symbol"])
        if not sid:
            continue
        as_of = r["as_of_date"].date() if hasattr(r["as_of_date"], "date") else r["as_of_date"]
        if db.query(FundamentalMetric).filter_by(stock_id=sid, as_of_date=as_of).first():
            continue
        batch.append(
            FundamentalMetric(
                stock_id=sid,
                as_of_date=as_of,
                market_cap_cr=r["market_cap_cr"],
                pe_ratio=r["pe_ratio"],
                pb_ratio=r["pb_ratio"],
                roe_pct=r["roe"],
                roce_pct=r["roce"],
                roa_pct=r["roa"],
                debt_to_equity=r["debt_to_equity"],
                current_ratio=r["current_ratio"],
                dividend_yield_pct=r["dividend_yield"],
                revenue_growth_pct=r["revenue_growth"],
                pat_margin_pct=r["pat_margin"],
                pat_cr=r["pat"],
            )
        )
        if len(batch) >= 2000:
            db.add_all(batch)
            db.commit()
            batch = []
    if batch:
        db.add_all(batch)
        db.commit()

    print("Loading benchmark...")
    for _, r in benchmark.iterrows():
        td = r["trade_date"].date() if hasattr(r["trade_date"], "date") else r["trade_date"]
        if db.query(BenchmarkData).filter_by(benchmark_name="NIFTY50", trade_date=td).first():
            continue
        db.add(
            BenchmarkData(
                benchmark_name="NIFTY50",
                trade_date=td,
                close=r["close"],
                adj_close=r["adj_close"],
            )
        )
    db.commit()
    db.close()
    print("Done — PostgreSQL populated. Run ingest_data --all later for live Yahoo data.")


if __name__ == "__main__":
    main()
