#!/usr/bin/env python3
"""Ingest real market data from Yahoo Finance into PostgreSQL."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.database.connection import SessionLocal, engine, Base
from app.data_collection.yahoo_finance import YahooFinanceCollector

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Ingest Yahoo Finance data into PostgreSQL")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--prices", action="store_true")
    parser.add_argument("--fundamentals", action="store_true")
    parser.add_argument("--benchmarks", action="store_true")
    parser.add_argument("--start-date", default="2015-01-01")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of stocks (for testing)")
    args = parser.parse_args()

    if not any([args.all, args.seed, args.prices, args.fundamentals, args.benchmarks]):
        parser.print_help()
        sys.exit(1)

    settings = get_settings()
    if not settings.use_database:
        logger.warning("USE_DATABASE is false — set USE_DATABASE=true in .env")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    collector = YahooFinanceCollector(db)

    try:
        if args.all or args.seed:
            n = collector.seed_companies(limit=args.limit)
            logger.info("Seeded %d stocks", n)

        if args.all or args.prices:
            logger.info("Fetching OHLCV price data from Yahoo Finance...")
            r = collector.fetch_all_prices(start_date=args.start_date, limit=args.limit)
            logger.info("Price records: %d, errors: %d", r["records"], len(r["errors"]))

        if args.all or args.fundamentals:
            logger.info("Fetching fundamentals from Yahoo Finance...")
            r = collector.fetch_fundamentals(limit=args.limit)
            logger.info("Fundamental records: %d, errors: %d", r["records"], len(r["errors"]))

        if args.all or args.benchmarks:
            logger.info("Fetching Nifty 50 benchmark...")
            r = collector.fetch_benchmarks(start_date=args.start_date)
            logger.info("Benchmark records: %d", r["records"])

    finally:
        db.close()


if __name__ == "__main__":
    main()
