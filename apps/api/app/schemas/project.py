from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

ProjectStatus = Literal[
    "draft",
    "brief_confirmed",
    "bible_ready",
    "season_planned",
    "episode_writing",
    "storyboard_ready",
    "visual_generating",
    "visual_approved",
    "audio_ready",
    "cut_ready",
    "qa_approved",
    "published",
    "needs_revision",
]


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    source_mode: Literal["adaptation", "original"] = "adaptation"
    genre: Optional[str] = None
    target_platform: str
    target_audience: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    source_mode: Literal["adaptation", "original"]
    genre: Optional[str] = None
    target_platform: str
    target_audience: Optional[str] = None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class CreateEpisodeRequest(BaseModel):
    episode_no: int = Field(ge=1)
    title: Optional[str] = Field(default=None, max_length=200)
    target_duration_sec: int = Field(ge=15, le=300)


class EpisodeResponse(BaseModel):
    id: UUID
    project_id: UUID
    episode_no: int
    title: Optional[str] = None
    status: ProjectStatus
    current_stage: str
    target_duration_sec: int
    created_at: datetime
    updated_at: datetime
