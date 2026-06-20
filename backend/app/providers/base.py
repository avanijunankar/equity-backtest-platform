from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class DataProvider(ABC):
    """Abstract data access layer — implemented by Demo and Database providers."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    def get_metrics_as_of(self, as_of: date) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_prices(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_benchmark_prices(self, name: str, start: date, end: date) -> pd.DataFrame:
        pass

    @abstractmethod
    def list_companies(self) -> pd.DataFrame:
        pass

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

    def health_check(self) -> dict:
        return {"status": "healthy", "source": self.source_name}
