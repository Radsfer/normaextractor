"""Health check público (sem autenticação)."""
import time

from fastapi import APIRouter

from app import deps
from app.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])

_START_TIME = time.monotonic()


def _rss_mb() -> float:
    try:
        import psutil

        proc = psutil.Process()
        return round(proc.memory_info().rss / (1024 * 1024), 2)
    except Exception:  # noqa: BLE001
        return -1.0


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    loaded = deps.is_model_loaded()
    settings = deps.get_settings()
    return HealthResponse(
        status="ok",
        model_loaded=loaded,
        model_version=settings.model_version,
        rss_mb=_rss_mb(),
        uptime_seconds=round(time.monotonic() - _START_TIME, 2),
    )
