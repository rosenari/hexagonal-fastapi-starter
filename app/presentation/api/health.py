"""Health check API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hexagonal-fastapi-starter",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }