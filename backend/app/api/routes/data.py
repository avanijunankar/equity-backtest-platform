import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.connection import SessionLocal
from app.providers.factory import get_data_provider, get_optional_db_session
from app.services.data_loader import DataLoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data", tags=["data"])


def _run_sync():
    db = SessionLocal()
    try:
        from app.data_collection.yahoo_finance import YahooFinanceCollector
        c = YahooFinanceCollector(db)
        c.seed_companies()
        c.fetch_all_prices()
        c.fetch_fundamentals()
        c.fetch_benchmarks()
    finally:
        db.close()


@router.get("/health")
def health_check(db: Session | None = Depends(get_optional_db_session)):
    settings = get_settings()
    provider = get_data_provider(db)
    health = provider.health_check()
    stats = {}
    if settings.use_database and db is not None:
        try:
            stats = DataLoader(db).get_data_stats()
        except Exception:
            pass
    return {
        "status": health.get("status", "healthy"),
        "data_source": provider.source_name,
        "use_database": settings.use_database,
        "stats": stats,
        **health,
    }


@router.get("/stats")
def data_stats(db: Session | None = Depends(get_optional_db_session)):
    if db is None:
        return {"message": "Database not configured"}
    return DataLoader(db).get_data_stats()


@router.post("/sync")
def sync_data(background_tasks: BackgroundTasks, db: Session | None = Depends(get_optional_db_session)):
    settings = get_settings()
    if not settings.use_database or db is None:
        raise HTTPException(
            status_code=400,
            detail="Set USE_DATABASE=true and ensure PostgreSQL is running",
        )
    from app.data_collection.yahoo_finance import YahooFinanceCollector
    collector = YahooFinanceCollector(db)
    collector.seed_companies()
    prices = collector.fetch_all_prices()
    fundamentals = collector.fetch_fundamentals()
    benchmarks = collector.fetch_benchmarks()
    return {
        "status": "completed",
        "source": "yahoo_finance",
        "prices": prices,
        "fundamentals": fundamentals,
        "benchmarks": benchmarks,
    }


@router.post("/sync/background")
def sync_background(background_tasks: BackgroundTasks):
    settings = get_settings()
    if not settings.use_database:
        raise HTTPException(status_code=400, detail="Database not enabled")
    background_tasks.add_task(_run_sync)
    return {"status": "started", "message": "Yahoo Finance sync running in background"}
