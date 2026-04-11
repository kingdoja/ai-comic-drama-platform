"""
QA Report API endpoints
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.qa_repository import QARepository
from app.schemas.qa import (
    IssueDetail,
    QAReportListItem,
    QAReportListResponse,
    QAReportResponse,
)

router = APIRouter(prefix="/api", tags=["qa"])


@router.get("/episodes/{episode_id}/qa-reports", response_model=QAReportListResponse)
async def list_qa_reports(
    episode_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all QA reports for an episode.
    
    Returns reports in reverse chronological order (newest first).
    
    Requirements: 10.1, 10.5
    """
    qa_repo = QARepository(db)
    
    reports = qa_repo.list_for_episode(episode_id)
    
    report_items = [
        QAReportListItem(
            id=report.id,
            qa_type=report.qa_type,
            target_ref_type=report.target_ref_type,
            target_ref_id=report.target_ref_id,
            result=report.result,
            severity=report.severity,
            issue_count=report.issue_count,
            score=float(report.score) if report.score is not None else None,
            created_at=report.created_at,
        )
        for report in reports
    ]
    
    return QAReportListResponse(
        episode_id=episode_id,
        reports=report_items,
        total_count=len(report_items),
    )


@router.get("/qa-reports/{report_id}", response_model=QAReportResponse)
async def get_qa_report(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed QA report by ID.
    
    Includes all issues found during the QA check.
    
    Requirements: 10.2, 10.3
    """
    qa_repo = QARepository(db)
    
    report = qa_repo.get_by_id(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="QA report not found")
    
    # Parse issues from JSONB
    issues = [
        IssueDetail(
            type=issue.get("type", "unknown"),
            severity=issue.get("severity", "info"),
            location=issue.get("location", ""),
            message=issue.get("message", ""),
            suggestion=issue.get("suggestion"),
        )
        for issue in (report.issues_jsonb or [])
    ]
    
    return QAReportResponse(
        id=report.id,
        project_id=report.project_id,
        episode_id=report.episode_id,
        stage_task_id=report.stage_task_id,
        qa_type=report.qa_type,
        target_ref_type=report.target_ref_type,
        target_ref_id=report.target_ref_id,
        result=report.result,
        score=float(report.score) if report.score is not None else None,
        severity=report.severity,
        issue_count=report.issue_count,
        issues=issues,
        rerun_stage_type=report.rerun_stage_type,
        created_at=report.created_at,
    )
