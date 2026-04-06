from typing import Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "service": "thinking-api"}
