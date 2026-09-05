"""Liveness/readiness check — the one endpoint Phase 2 must prove end-to-end:
API reachable, and API-to-database connectivity verified without crashing
the request if the database happens to be down.
"""
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


class HealthData(BaseModel):
    api: str
    database: str
    environment: str


class HealthResponse(BaseModel):
    data: HealthData


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    settings = get_settings()
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:  # noqa: BLE001 — deliberately broad: any DB failure means "unreachable", never a 500
        logger.exception("Database health check failed")
        database_status = "unreachable"

    return HealthResponse(
        data=HealthData(api="ok", database=database_status, environment=settings.environment)
    )
