"""Resolve data provider: PostgreSQL (real data) or demo fallback."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.providers.base import DataProvider
from app.providers.demo import DemoDataProvider

logger = logging.getLogger(__name__)

_demo_provider: Optional[DemoDataProvider] = None


def get_data_provider(db: Session | None = None) -> DataProvider:
    settings = get_settings()

    if settings.use_database and db is not None:
        try:
            from app.providers.database import DatabaseDataProvider
            provider = DatabaseDataProvider(db)
            health = provider.health_check()
            if health.get("status") == "healthy" and health.get("companies", 0) > 0:
                return provider
            if health.get("companies", 0) == 0:
                logger.warning("PostgreSQL connected but empty — run: python -m scripts.ingest_data --all")
        except Exception as exc:
            logger.warning("Database error: %s", exc)

    global _demo_provider
    if _demo_provider is None:
        logger.info("Falling back to demo provider")
        _demo_provider = DemoDataProvider()
    return _demo_provider


def get_optional_db_session():
    settings = get_settings()
    if not settings.use_database:
        yield None
        return
    from app.database.connection import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
