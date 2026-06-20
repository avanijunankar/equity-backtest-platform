import pytest


@pytest.fixture(autouse=True)
def demo_mode(monkeypatch):
    """Tests run without requiring live PostgreSQL."""
    monkeypatch.setenv("USE_DATABASE", "false")
    from app.core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
