from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.project import EpisodeResponse, ProjectResponse
from app.schemas.workflow import WorkflowRunResponse

DocumentStatus = Literal["draft", "approved", "archived", "ready", "pending"]
AssetType = Literal[
    "character_reference",
    "scene_reference",
    "shot_image",
    "audio_voice",
    "subtitle_file",
    "preview_video",
    "final_video",
    "cover_image",
    "export_bundle",
]
QAResult = Literal["pass", "fail", "warn", "pending"]


class DocumentSummaryResponse(BaseModel):
    id: UUID
    document_type: str
    version: int
    status: DocumentStatus
    title: str | None = None
    summary_text: str | None = None
    updated_at: datetime | None = None


class AssetSummaryResponse(BaseModel):
    id: UUID
    asset_type: AssetType
    storage_key: str
    mime_type: str
    size_bytes: int
    duration_ms: int | None = None
    width: int | None = None
    height: int | None = None
    is_selected: bool = False
    version: int = 1
    created_at: datetime | None = None


class ShotSummaryResponse(BaseModel):
    code: str
    duration_ms: int
    status: str


class QAReportSummaryResponse(BaseModel):
    id: UUID
    qa_type: str
    result: QAResult
    severity: str
    issue_count: int
    rerun_stage_type: str | None = None
    created_at: datetime | None = None


class WorkspaceQAResponse(BaseModel):
    result: QAResult
    issue_count: int
    reports: list[QAReportSummaryResponse] = Field(default_factory=list)


class EpisodeWorkspaceResponse(BaseModel):
    project: ProjectResponse
    episode: EpisodeResponse
    documents: list[DocumentSummaryResponse] = Field(default_factory=list)
    shots: list[ShotSummaryResponse] = Field(default_factory=list)
    assets: list[AssetSummaryResponse] = Field(default_factory=list)
    qa_summary: WorkspaceQAResponse
    latest_workflow: WorkflowRunResponse | None = None
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
