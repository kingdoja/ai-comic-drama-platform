from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UpdateDocumentRequest(BaseModel):
    """Request to update a document's content."""
    content_jsonb: Dict[str, Any] = Field(description="Updated document content")
    user_id: UUID = Field(description="ID of the user making the edit")


class DocumentResponse(BaseModel):
    """Response containing document details."""
    id: UUID
    project_id: UUID
    episode_id: Optional[UUID]
    stage_task_id: Optional[UUID]
    document_type: str
    version: int
    status: str
    title: Optional[str]
    content_jsonb: Dict[str, Any]
    summary_text: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
