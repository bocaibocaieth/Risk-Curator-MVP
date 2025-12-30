"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import assets, ratings, alerts, monitor

router = APIRouter()

router.include_router(assets.router, prefix="/assets", tags=["Assets"])
router.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])
router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
router.include_router(monitor.router, prefix="/monitor", tags=["Monitor"])
