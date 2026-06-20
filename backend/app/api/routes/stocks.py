from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.providers.factory import get_data_provider, get_optional_db_session

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/")
def list_stocks(db: Session | None = Depends(get_optional_db_session)):
    provider = get_data_provider(db)
    df = provider.list_companies()
    return df.to_dict(orient="records") if not df.empty else []


@router.get("/metrics")
def list_available_metrics(db: Session | None = Depends(get_optional_db_session)):
    provider = get_data_provider(db)
    return {"metrics": provider.get_available_metrics()}
