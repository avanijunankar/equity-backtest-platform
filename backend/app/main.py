import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import backtest, data, stocks
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title="Equity Backtesting Platform",
    description="Production-grade fundamental strategy backtesting for Indian equities",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest.router)
app.include_router(stocks.router)
app.include_router(data.router)


@app.get("/")
def root():
    return {
        "name": "Equity Backtesting Platform API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/data/health",
        "mode": "database" if settings.use_database else "demo",
    }
