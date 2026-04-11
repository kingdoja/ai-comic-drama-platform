from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.models import (
    AssetModel,
    DocumentModel,
    EpisodeModel,
    ProjectModel,
    QAReportModel,
    ReviewDecisionModel,
    ShotModel,
    StageTaskModel,
    WorkflowRunModel,
)
from app.repositories.asset_repository import AssetRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.episode_repository import EpisodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.qa_repository import QARepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.shot_repository import ShotRepository
from app.repositories.stage_task_repository import StageTaskRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.project import CreateEpisodeRequest, CreateProjectRequest, EpisodeResponse, ProjectResponse
from app.schemas.workflow import StartEpisodeWorkflowRequest, WorkflowRunResponse
from app.schemas.workspace import (
    AssetSummaryResponse,
    DocumentSummaryResponse,
    EpisodeWorkspaceResponse,
    FailedStageInfo,
    MediaStatusResponse,
    PrimaryAssetInfo,
    QAReportSummaryResponse,
    ReviewDecisionSummaryResponse,
    ShotSummaryResponse,
    StageTaskSummaryResponse,
    SubmitReviewDecisionRequest,
    WorkspaceQAResponse,
    WorkspaceReviewResponse,
)
from app.services.review_service import ReviewGateService
from app.services.workflow_service import WorkflowService


def _to_project_response(project: ProjectModel) -> ProjectResponse:
    return ProjectResponse.model_validate(project, from_attributes=True)


def _to_episode_response(episode: EpisodeModel) -> EpisodeResponse:
    return EpisodeResponse.model_validate(episode, from_attributes=True)


def _to_workflow_response(workflow: Optional[WorkflowRunModel]) -> Optional[WorkflowRunResponse]:
    if workflow is None:
        return None
    return WorkflowRunResponse.model_validate(workflow, from_attributes=True)


def _to_document_summary(document: DocumentModel) -> DocumentSummaryResponse:
    return DocumentSummaryResponse(
        id=document.id,
        document_type=document.document_type,
        version=document.version,
        status=document.status,
        title=document.title,
        summary_text=document.summary_text,
        updated_at=document.updated_at,
    )


def _to_asset_summary(asset: AssetModel) -> AssetSummaryResponse:
    quality_score = float(asset.quality_score) if isinstance(asset.quality_score, Decimal) else asset.quality_score
    return AssetSummaryResponse(
        id=asset.id,
        asset_type=asset.asset_type,
        storage_key=asset.storage_key,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        duration_ms=asset.duration_ms,
        width=asset.width,
        height=asset.height,
        is_selected=asset.is_selected,
        version=asset.version,
        created_at=asset.created_at,
    )


def _to_stage_task_summary(stage_task: StageTaskModel) -> StageTaskSummaryResponse:
    return StageTaskSummaryResponse(
        id=stage_task.id,
        stage_type=stage_task.stage_type,
        task_status=stage_task.task_status,
        worker_kind=stage_task.worker_kind,
        review_required=stage_task.review_required,
        review_status=stage_task.review_status,
        started_at=stage_task.started_at,
        finished_at=stage_task.finished_at,
        error_message=stage_task.error_message,
    )


def _to_shot_summary(
    shot: ShotModel,
    visual_spec_doc_id: Optional[UUID] = None,
    primary_assets: Optional[Dict[str, "PrimaryAssetInfo"]] = None,
) -> ShotSummaryResponse:
    # Extract visual_constraints summary
    visual_constraints = shot.visual_constraints_jsonb or {}
    visual_constraints_summary = None
    if visual_constraints:
        visual_constraints_summary = {
            "render_prompt": visual_constraints.get("render_prompt", "")[:200] if visual_constraints.get("render_prompt") else "",
            "style_keywords": visual_constraints.get("style_keywords", []),
            "composition": visual_constraints.get("composition", ""),
            "character_refs": visual_constraints.get("character_refs", []),
        }
    
    return ShotSummaryResponse(
        id=shot.id,
        code=shot.shot_code,
        shot_index=shot.shot_no,
        scene_no=shot.scene_no,
        shot_no=shot.shot_no,
        title=shot.action_text,
        duration_ms=shot.duration_ms,
        status=shot.status,
        camera_size=shot.camera_size,
        camera_angle=shot.camera_angle,
        movement_type=shot.movement_type,
        characters=shot.characters_jsonb or [],
        visual_constraints_summary=visual_constraints_summary,
        visual_spec_doc_id=visual_spec_doc_id,
        stage_task_id=shot.stage_task_id,
        version=shot.version,
        updated_at=shot.updated_at,
        primary_assets=primary_assets or {},
    )


def _to_qa_summary(report: QAReportModel) -> QAReportSummaryResponse:
    return QAReportSummaryResponse(
        id=report.id,
        qa_type=report.qa_type,
        result=report.result,
        severity=report.severity,
        issue_count=report.issue_count,
        rerun_stage_type=report.rerun_stage_type,
        created_at=report.created_at,
    )


def _to_review_summary(review: ReviewDecisionModel) -> ReviewDecisionSummaryResponse:
    return ReviewDecisionSummaryResponse(
        id=review.id,
        status=review.decision,
        decision_note=review.comment_text,
        stage_task_id=review.stage_task_id,
        created_at=review.created_at,
    )


def _build_primary_assets_for_shot(
    shot_id: UUID,
    all_assets: List[AssetModel],
) -> Dict[str, PrimaryAssetInfo]:
    """
    Build a dict of primary (selected) assets keyed by asset_type for a shot.

    Implements Requirement 15.2
    """
    result: Dict[str, PrimaryAssetInfo] = {}
    for asset in all_assets:
        if asset.shot_id == shot_id and asset.is_selected:
            result[asset.asset_type] = PrimaryAssetInfo(
                asset_id=asset.id,
                asset_type=asset.asset_type,
                storage_key=asset.storage_key,
                mime_type=asset.mime_type,
                duration_ms=asset.duration_ms,
                width=asset.width,
                height=asset.height,
                created_at=asset.created_at,
            )
    return result


# Media stage types that belong to the media pipeline
_MEDIA_STAGE_TYPES = {"image_render", "subtitle", "tts", "edit_export_preview"}


def _build_media_status(
    stage_tasks: List[StageTaskModel],
    all_assets: List[AssetModel],
    latest_workflow: Optional["WorkflowRunModel"],
) -> MediaStatusResponse:
    """
    Derive media pipeline status from stage tasks and assets.

    Implements Requirements: 15.1, 15.3, 15.4, 15.5
    """
    media_tasks = [t for t in stage_tasks if t.stage_type in _MEDIA_STAGE_TYPES]

    if not media_tasks:
        return MediaStatusResponse(status="not_started")

    # Collect failed stages for display (Requirement 15.5)
    failed_stages = [
        FailedStageInfo(
            stage_type=t.stage_type,
            stage_task_id=t.id,
            error_message=t.error_message,
            failed_at=t.finished_at,
        )
        for t in media_tasks
        if t.task_status == "failed"
    ]

    # Determine running stage (Requirement 15.4)
    running_task = next((t for t in media_tasks if t.task_status == "running"), None)
    current_stage = running_task.stage_type if running_task else None

    # Find preview asset
    preview_asset = next(
        (a for a in all_assets if a.asset_type in ("preview", "preview_video") and a.is_selected),
        None,
    )
    # Fall back to any preview asset if none is selected
    if preview_asset is None:
        preview_asset = next(
            (a for a in all_assets if a.asset_type in ("preview", "preview_video")),
            None,
        )

    preview_url = preview_asset.storage_key if preview_asset else None
    preview_asset_id = preview_asset.id if preview_asset else None
    preview_duration_ms = preview_asset.duration_ms if preview_asset else None

    # Determine overall media status
    statuses = {t.task_status for t in media_tasks}
    if "running" in statuses or "pending" in statuses:
        status = "generating"
    elif failed_stages and preview_asset is None:
        # All failed, nothing produced
        status = "failed"
    elif failed_stages:
        # Some failed but preview exists
        status = "partial"
    elif preview_asset is not None:
        status = "ready"
    else:
        # Tasks succeeded but no preview yet (e.g. only image_render done)
        status = "partial"

    return MediaStatusResponse(
        status=status,
        current_stage=current_stage,
        preview_url=preview_url,
        preview_asset_id=preview_asset_id,
        preview_duration_ms=preview_duration_ms,
        failed_stages=failed_stages,
    )


class DatabaseStore:
    def __init__(self, db: Session) -> None:
        self.projects = ProjectRepository(db)
        self.episodes = EpisodeRepository(db)
        self.workflows = WorkflowRepository(db)
        self.documents = DocumentRepository(db)
        self.assets = AssetRepository(db)
        self.qa_reports = QARepository(db)
        self.stage_tasks = StageTaskRepository(db)
        self.shots = ShotRepository(db)
        self.reviews = ReviewRepository(db)
        self.workflow_service = WorkflowService(db, self.workflows, self.stage_tasks, self.documents, self.shots, self.episodes)
        self.review_service = ReviewGateService(db, self.reviews, self.stage_tasks, self.workflows)

    def create_project(self, payload: CreateProjectRequest) -> ProjectResponse:
        return _to_project_response(self.projects.create(payload))

    def list_projects(self) -> List[ProjectResponse]:
        return [_to_project_response(item) for item in self.projects.list()]

    def get_project(self, project_id):
        project = self.projects.get(project_id)
        return _to_project_response(project) if project else None

    def create_episode(self, project_id, payload: CreateEpisodeRequest) -> EpisodeResponse:
        return _to_episode_response(self.episodes.create(project_id, payload))

    def get_episode(self, episode_id):
        episode = self.episodes.get(episode_id)
        return _to_episode_response(episode) if episode else None

    def start_workflow(self, project_id, episode_id, payload: StartEpisodeWorkflowRequest) -> WorkflowRunResponse:
        workflow = self.workflow_service.start_episode_workflow(project_id, episode_id, payload)
        return _to_workflow_response(workflow)

    def latest_workflow_for_episode(self, episode_id):
        return _to_workflow_response(self.workflows.latest_for_episode(episode_id))

    def submit_review_decision(
        self,
        project_id,
        episode_id,
        payload: SubmitReviewDecisionRequest,
    ) -> ReviewDecisionSummaryResponse:
        review = self.review_service.submit_review_decision(project_id, episode_id, payload)
        return _to_review_summary(review)

    def build_workspace(self, project_id, episode_id) -> Optional[EpisodeWorkspaceResponse]:
        project = self.get_project(project_id)
        episode = self.get_episode(episode_id)
        if not project or not episode:
            return None

        latest_workflow = self.workflows.latest_for_episode(episode_id)
        
        # Query documents once and reuse
        all_documents = self.documents.list_for_episode(episode_id)
        documents = [_to_document_summary(item) for item in all_documents]

        selected_assets = self.assets.list_selected_for_episode(episode_id)
        assets_source = selected_assets if selected_assets else self.assets.list_for_episode(episode_id)
        assets = [_to_asset_summary(item) for item in assets_source]

        # Fetch all assets for primary_assets lookup (Requirement 15.2)
        all_assets_models = self.assets.list_for_episode(episode_id)

        # Fetch QA reports and calculate critical issue count
        qa_report_models = self.qa_reports.list_for_episode(episode_id)
        qa_reports = [_to_qa_summary(item) for item in qa_report_models]
        
        # Calculate critical issue count for QA summary
        critical_issue_count = sum(
            item.issue_count 
            for item in qa_report_models 
            if item.severity == "critical"
        )
        
        if latest_workflow:
            stage_task_models = self.stage_tasks.list_for_workflow(latest_workflow.id)
        else:
            stage_task_models = self.stage_tasks.list_for_episode(episode_id)
        stage_tasks = [_to_stage_task_summary(item) for item in stage_task_models]

        # Find the latest visual_spec document from already-queried documents
        visual_spec_doc_id = None
        visual_spec_docs = [
            doc for doc in all_documents
            if doc.document_type == "visual_spec"
        ]
        if visual_spec_docs:
            # Sort by version descending to get the latest
            visual_spec_docs.sort(key=lambda d: d.version, reverse=True)
            visual_spec_doc_id = visual_spec_docs[0].id

        # Query shots and attach primary assets per shot (Requirements 15.2, 15.3)
        shot_models = self.shots.list_current_for_episode(episode_id)
        shots = [
            _to_shot_summary(
                item,
                visual_spec_doc_id,
                _build_primary_assets_for_shot(item.id, all_assets_models),
            )
            for item in shot_models
        ]

        reviews = [_to_review_summary(item) for item in self.reviews.list_for_episode(episode_id)]

        # Calculate QA result and issue count
        qa_result = "pending"
        issue_count = 0
        if qa_reports:
            qa_result = qa_reports[0].result
            issue_count = sum(item.issue_count for item in qa_reports)

        # Calculate rerun count - count workflows with rerun_from_stage set
        all_workflows = self.workflows.list_for_episode(episode_id)
        rerun_count = sum(1 for wf in all_workflows if wf.rerun_from_stage is not None)

        pending_review_count = sum(
            1
            for task in stage_tasks
            if task.review_required
            and task.task_status == "succeeded"
            and task.review_status in (None, "pending")
        )
        latest_decision = reviews[0] if reviews else None

        if pending_review_count > 0:
            review_summary = WorkspaceReviewResponse(
                status="pending",
                pending_count=pending_review_count,
                latest_decision=latest_decision,
            )
        elif latest_decision is not None:
            review_summary = WorkspaceReviewResponse(
                status=latest_decision.status,
                pending_count=0,
                latest_decision=latest_decision,
            )
        else:
            review_summary = WorkspaceReviewResponse()

        # Build media status from all stage tasks for the episode (Requirement 15.1)
        all_stage_task_models = self.stage_tasks.list_for_episode(episode_id)
        media_status = _build_media_status(all_stage_task_models, all_assets_models, latest_workflow)

        return EpisodeWorkspaceResponse(
            project=project,
            episode=episode,
            documents=documents,
            stage_tasks=stage_tasks,
            shots=shots,
            assets=assets,
            qa_summary=WorkspaceQAResponse(
                result=qa_result,
                issue_count=issue_count,
                critical_issue_count=critical_issue_count,
                has_critical_issues=critical_issue_count > 0,
                reports=qa_reports,
            ),
            review_summary=review_summary,
            rerun_count=rerun_count,
            latest_workflow=_to_workflow_response(latest_workflow),
            media_status=media_status,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "mode": "database-backed-workspace",
                "shots_mode": "current-version-db-query",
                "assets_mode": "selected-first",
                "visual_spec_doc_id": str(visual_spec_doc_id) if visual_spec_doc_id else None,
            },
        )
