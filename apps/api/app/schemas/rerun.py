"""
Rerun schemas for API requests and responses

Implements Requirements 7.1, 8.1, 12.1
"""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RerunWorkflowRequest(BaseModel):
    """
    Request to rerun a workflow from a specified stage.
    
    Requirements: 7.1, 7.2
    """
    from_stage: str = Field(
        description="Stage to start rerun from (e.g., 'brief', 'script', 'image_render')"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for the rerun"
    )


class RerunShotsRequest(BaseModel):
    """
    Request to rerun specific shots at a given stage.
    
    Requirements: 8.1, 8.2
    """
    shot_ids: List[UUID] = Field(
        description="List of shot IDs to rerun"
    )
    stage_type: Literal["image_render", "tts"] = Field(
        description="Stage type to rerun for the specified shots"
    )


class RerunWorkflowResponse(BaseModel):
    """
    Response after creating a rerun workflow.
    
    Requirements: 7.1, 7.2
    """
    id: UUID = Field(description="WorkflowRun ID")
    episode_id: UUID
    workflow_kind: str
    status: str
    rerun_from_stage: Optional[str] = None
    parent_workflow_run_id: Optional[UUID] = None
    rerun_reason: Optional[str] = None
    rerun_shot_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Shot IDs for shot-level reruns"
    )
    started_at: datetime


class RerunHistoryItem(BaseModel):
    """
    Single rerun item in history list.
    
    Requirements: 12.1, 12.2, 12.3
    """
    id: UUID
    workflow_kind: str
    status: str
    rerun_from_stage: Optional[str] = Field(
        default=None,
        description="Stage where rerun started (null for initial runs)"
    )
    parent_workflow_run_id: Optional[UUID] = Field(
        default=None,
        description="Parent workflow run ID (null for initial runs)"
    )
    rerun_reason: Optional[str] = None
    rerun_shot_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Shot IDs for shot-level reruns (null for full reruns)"
    )
    is_rerun: bool = Field(
        description="True if this is a rerun, False if initial run"
    )
    started_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


class RerunHistoryResponse(BaseModel):
    """
    List of workflow runs (including reruns) for an episode.
    
    Requirements: 12.1, 12.2, 12.3
    """
    episode_id: UUID
    workflow_runs: List[RerunHistoryItem] = Field(default_factory=list)
    total_count: int = Field(description="Total number of workflow runs")
    rerun_count: int = Field(description="Number of reruns (excluding initial runs)")
