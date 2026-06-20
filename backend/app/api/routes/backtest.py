import io
import logging
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.backtest.engine import BacktestEngine
from app.providers.factory import get_data_provider, get_optional_db_session
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.services.prebuilt_strategies import PREBUILT_STRATEGIES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/backtest", tags=["backtest"])


def _run_engine(config: dict, db: Session | None) -> dict:
    provider = get_data_provider(db)
    engine = BacktestEngine(provider)
    return engine.run(config)


@router.post("/run", response_model=BacktestResponse)
def run_backtest(
    request: BacktestRequest,
    db: Session | None = Depends(get_optional_db_session),
):
    try:
        result = _run_engine(request.model_dump(mode="json"), db)
        return BacktestResponse(**result)
    except Exception as exc:
        logger.exception("Backtest failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/strategies")
def list_prebuilt_strategies():
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "config": s["config"].model_dump(mode="json"),
        }
        for s in PREBUILT_STRATEGIES
    ]


@router.post("/strategies/{strategy_id}/run", response_model=BacktestResponse)
def run_prebuilt_strategy(
    strategy_id: str,
    db: Session | None = Depends(get_optional_db_session),
):
    strategy = next((s for s in PREBUILT_STRATEGIES if s["id"] == strategy_id), None)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    result = _run_engine(strategy["config"].model_dump(mode="json"), db)
    return BacktestResponse(**result)


@router.get("/history")
def backtest_history():
    return {"runs": [], "message": "History persisted when USE_DATABASE=true and migrations applied"}


@router.get("/{run_id}")
def get_backtest_run(run_id: str):
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found — enable database for persistence")


@router.post("/compare")
def compare_strategies(
    requests: list[BacktestRequest],
    db: Session | None = Depends(get_optional_db_session),
):
    if len(requests) < 2 or len(requests) > 5:
        raise HTTPException(status_code=400, detail="Provide 2-5 strategies to compare")

    results = []
    for i, req in enumerate(requests):
        result = _run_engine(req.model_dump(mode="json"), db)
        results.append(
            {
                "label": f"Strategy {i + 1}",
                "performance": result.get("performance", {}),
                "equity_curve": result.get("equity_curve", []),
            }
        )
    return {"comparisons": results}


@router.post("/export/csv")
def export_csv(data: dict[str, Any]):
    equity = data.get("equity_curve", [])
    if not equity:
        raise HTTPException(status_code=400, detail="No equity curve data")
    df = pd.DataFrame(equity)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=backtest_results.csv"},
    )


@router.post("/export")
def export_results(data: dict[str, Any]):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if data.get("equity_curve"):
            pd.DataFrame(data["equity_curve"]).to_excel(writer, sheet_name="Equity Curve", index=False)
        if data.get("portfolio_logs"):
            flat = []
            for log in data["portfolio_logs"]:
                for h in log.get("holdings", []):
                    flat.append({"date": log["date"], "portfolio_value": log["portfolio_value"], **h})
            if flat:
                pd.DataFrame(flat).to_excel(writer, sheet_name="Holdings", index=False)
        if data.get("transactions"):
            pd.DataFrame(data["transactions"]).to_excel(writer, sheet_name="Transactions", index=False)
        if data.get("performance"):
            pd.DataFrame([data["performance"]]).to_excel(writer, sheet_name="Performance", index=False)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=backtest_results.xlsx"},
    )
