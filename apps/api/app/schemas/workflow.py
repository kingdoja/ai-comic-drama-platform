from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

WorkflowStatus = Literal["pending", "running", "waiting_review", "succeeded", "failed"]
StageType = Literal[
    "brief",
    "story_bible",
    "character",
    "script",
    "storyboard",
    "visual_spec",
    "image_render",
    "subtitle",
    "tts",
    "edit_export_preview",
    "qa",
    "human_review_gate",
    "export_final",
]


class StartEpisodeWorkflowRequest(BaseModel):
    start_stage: StageType = Field(default="brief")


class RerunStageRequest(BaseModel):
    rerun_stage: StageType
    target_shot_ids: List[UUID] = Field(default_factory=list)


class WorkflowRunResponse(BaseModel):
    id: UUID
    project_id: UUID
    episode_id: UUID
    status: WorkflowStatus
    workflow_kind: str
    started_at: datetime
    finished_at: Optional[datetime] = None
