"""
Brief generation API endpoints
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.brief_service import BriefService

router = APIRouter(prefix="/api/brief", tags=["brief"])


class GenerateBriefRequest(BaseModel):
    """Request to generate a brief"""
    project_id: UUID
    episode_id: UUID
    raw_material: str
    platform: str = "douyin"
    target_duration_sec: int = 60
    target_audience: Optional[str] = None


class GenerateBriefResponse(BaseModel):
    """Response from brief generation"""
    success: bool
    document_id: Optional[UUID] = None
    brief: Optional[dict] = None
    error: Optional[str] = None
    token_usage: Optional[int] = None
    duration_ms: Optional[int] = None


@router.post("/generate", response_model=GenerateBriefResponse)
async def generate_brief(
    request: GenerateBriefRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a brief from raw material.
    
    This endpoint:
    1. Takes raw story material
    2. Calls Brief Agent with real LLM
    3. Saves the generated brief to database
    4. Returns the brief content
    """
    try:
        service = BriefService(db)
        
        result = service.generate_brief(
            project_id=request.project_id,
            episode_id=request.episode_id,
            raw_material=request.raw_material,
            platform=request.platform,
            target_duration_sec=request.target_duration_sec,
            target_audience=request.target_audience
        )
        
        return GenerateBriefResponse(
            success=True,
            document_id=result["document_id"],
            brief=result["content"],
            token_usage=result.get("token_usage"),
            duration_ms=result.get("duration_ms")
        )
        
    except Exception as e:
        return GenerateBriefResponse(
            success=False,
            error=str(e)
        )


@router.get("/{document_id}", response_model=dict)
async def get_brief(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a brief by document ID.
    """
    service = BriefService(db)
    
    brief = service.get_brief(document_id)
    
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    return brief
