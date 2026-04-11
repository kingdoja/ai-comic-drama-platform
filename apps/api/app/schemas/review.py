"""
Review schemas for API requests and responses

Implements Requirements 11.3, 6.1
"""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewSubmitRequest(BaseModel):
    """
    Request to submit a review decision.
    
    Requirements: 11.3, 6.1, 6.2
    """
    decision: Literal["approved", "rejected", "revision_required"] = Field(
        description="Review decision"
    )
    comment: Optional[str] = Field(
        default=None,
        description="Review comment or feedback"
    )
    payload: Optional[dict] = Field(
        default=None,
        description="Additional data (e.g., rerun parameters)"
    )


class ReviewDecisionResponse(BaseModel):
    """
    Response containing review decision details.
    
    Requirements: 11.3, 6.1
    """
    id: UUID
    project_id: UUID
    episode_id: UUID
    stage_task_id: UUID
    reviewer_user_id: Optional[UUID] = None
    decision: Literal["approved", "rejected", "revision_required"]
    comment_text: Optional[str] = None
    payload_jsonb: dict = Field(default_factory=dict)
    created_at: datetime


class ReviewHistoryItem(BaseModel):
    """
    Single review item in history list.
    
    Requirements: 12.1, 12.2
    """
    id: UUID
    stage_task_id: UUID
    stage_type: Optional[str] = Field(
        default=None,
        description="Type of stage that was reviewed"
    )
    reviewer_user_id: Optional[UUID] = None
    decision: Literal["approved", "rejected", "revision_required"]
    comment_text: Optional[str] = None
    created_at: datetime


class ReviewHistoryResponse(BaseModel):
    """
    List of review decisions for an episode.
    
    Requirements: 12.1, 12.2
    """
    episode_id: UUID
    reviews: List[ReviewHistoryItem] = Field(default_factory=list)
    total_count: int = Field(description="Total number of reviews")
