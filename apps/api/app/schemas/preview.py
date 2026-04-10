"""
Preview schemas for API requests and responses.

Implements Requirements: 14.1, 14.3, 14.4, 14.5
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PreviewAssetResponse(BaseModel):
    """Metadata for the preview video asset."""
    id: UUID
    storage_key: str
    mime_type: str
    size_bytes: int
    duration_ms: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PreviewStageTaskResponse(BaseModel):
    """Summary of the preview export stage task."""
    id: UUID
    task_status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class PreviewResponse(BaseModel):
    """
    Full preview response for an episode.

    Implements Requirements: 14.1, 14.5
    """
    episode_id: UUID
    # One of: "ready", "generating", "failed", "not_started"
    status: str
    preview_url: Optional[str] = None
    asset: Optional[PreviewAssetResponse] = None
    stage_task: Optional[PreviewStageTaskResponse] = None
    # Human-readable status message
    message: str
    generated_at: Optional[datetime] = None


class PreviewStatusResponse(BaseModel):
    """
    Preview generation status response.

    Implements Requirements: 14.3
    """
    episode_id: UUID
    status: str
    # Progress 0-100, None if not applicable
    progress_pct: Optional[int] = None
    current_stage: Optional[str] = None
    # ISO-8601 string or None
    estimated_completion_at: Optional[datetime] = None
    stage_tasks: List[PreviewStageTaskResponse] = Field(default_factory=list)
    message: str


class PreviewRetryResponse(BaseModel):
    """
    Response after triggering a preview retry.

    Implements Requirements: 14.4
    """
    episode_id: UUID
    stage_task_id: Optional[UUID] = None
    message: str
