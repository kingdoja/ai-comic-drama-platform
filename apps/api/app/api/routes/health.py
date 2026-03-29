from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "thinking-api"}
