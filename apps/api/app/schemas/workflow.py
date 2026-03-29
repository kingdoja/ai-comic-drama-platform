from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

WorkflowStatus = Literal["pending", "running", "waiting_review", "succeeded", "failed"]


class StartEpisodeWorkflowRequest(BaseModel):
    start_stage: str = Field(default="brief")


class RerunStageRequest(BaseModel):
    rerun_stage: str
    target_shot_ids: list[UUID] = Field(default_factory=list)


class WorkflowRunResponse(BaseModel):
    id: UUID
    project_id: UUID
    episode_id: UUID
    status: WorkflowStatus
    workflow_kind: str
    started_at: datetime
    finished_at: datetime | None = None
