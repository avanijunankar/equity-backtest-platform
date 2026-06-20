"""PostgreSQL data provider — used when USE_DATABASE=true."""

from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from app.providers.base import DataProvider
from app.services.data_loader import DataLoader


class DatabaseDataProvider(DataProvider):
    def __init__(self, db: Session):
        self._loader = DataLoader(db)

    @property
    def source_name(self) -> str:
        return "postgresql"

    def get_metrics_as_of(self, as_of: date) -> pd.DataFrame:
        return self._loader.get_metrics_as_of(as_of)

    def get_prices(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        return self._loader.get_prices(symbols, start, end)

    def get_benchmark_prices(self, name: str, start: date, end: date) -> pd.DataFrame:
        return self._loader.get_benchmark_prices(name, start, end)

    def list_companies(self) -> pd.DataFrame:
        return self._loader.list_companies()

    def get_available_metrics(self) -> list[str]:
        return self._loader.get_available_metrics()

    def health_check(self) -> dict:
        try:
            companies = self.list_companies()
            count = len(companies)
            return {
                "status": "healthy",
                "source": "postgresql",
                "companies": count,
                "has_data": count > 0,
            }
        except Exception as exc:
            return {"status": "unhealthy", "source": "postgresql", "error": str(exc)}
