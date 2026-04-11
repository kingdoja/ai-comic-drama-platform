"""
QA Report schemas for API responses
"""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class IssueDetail(BaseModel):
    """Individual issue found during QA check"""
    type: str = Field(description="Issue type (e.g., missing_field, invalid_format)")
    severity: Literal["info", "minor", "major", "critical"] = Field(description="Issue severity level")
    location: str = Field(description="Location of the issue (e.g., brief.genre, shot.3.dialogue)")
    message: str = Field(description="Human-readable issue description")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix or improvement")


class QAReportResponse(BaseModel):
    """Single QA report response"""
    id: UUID
    project_id: UUID
    episode_id: UUID
    stage_task_id: Optional[UUID] = None
    qa_type: str = Field(description="Type of QA check (rule_check, semantic_check, asset_check)")
    target_ref_type: str = Field(description="Type of target being checked (document, shot, asset, episode)")
    target_ref_id: Optional[UUID] = None
    result: Literal["passed", "failed", "warning"] = Field(description="Overall QA result")
    score: Optional[float] = Field(default=None, description="Quality score (0-100)")
    severity: Literal["info", "minor", "major", "critical"] = Field(description="Highest severity level found")
    issue_count: int = Field(description="Total number of issues found")
    issues: List[IssueDetail] = Field(default_factory=list, description="List of all issues found")
    rerun_stage_type: Optional[str] = Field(default=None, description="Suggested stage to rerun if QA failed")
    created_at: datetime


class QAReportListItem(BaseModel):
    """QA report summary for list view"""
    id: UUID
    qa_type: str
    target_ref_type: str
    target_ref_id: Optional[UUID] = None
    result: Literal["passed", "failed", "warning"]
    severity: Literal["info", "minor", "major", "critical"]
    issue_count: int
    score: Optional[float] = None
    created_at: datetime


class QAReportListResponse(BaseModel):
    """List of QA reports for an episode"""
    episode_id: UUID
    reports: List[QAReportListItem] = Field(default_factory=list)
    total_count: int = Field(description="Total number of reports")
