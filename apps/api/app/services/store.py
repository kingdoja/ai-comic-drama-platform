from datetime import UTC, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models import AssetModel, DocumentModel, EpisodeModel, ProjectModel, QAReportModel, WorkflowRunModel
from app.repositories.asset_repository import AssetRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.episode_repository import EpisodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.qa_repository import QARepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.project import CreateEpisodeRequest, CreateProjectRequest, EpisodeResponse, ProjectResponse
from app.schemas.workflow import StartEpisodeWorkflowRequest, WorkflowRunResponse
from app.schemas.workspace import (
    AssetSummaryResponse,
    DocumentSummaryResponse,
    EpisodeWorkspaceResponse,
    QAReportSummaryResponse,
    ShotSummaryResponse,
    WorkspaceQAResponse,
)


def _to_project_response(project: ProjectModel) -> ProjectResponse:
    return ProjectResponse.model_validate(project, from_attributes=True)


def _to_episode_response(episode: EpisodeModel) -> EpisodeResponse:
    return EpisodeResponse.model_validate(episode, from_attributes=True)


def _to_workflow_response(workflow: WorkflowRunModel | None) -> WorkflowRunResponse | None:
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


class DatabaseStore:
    def __init__(self, db: Session) -> None:
        self.projects = ProjectRepository(db)
        self.episodes = EpisodeRepository(db)
        self.workflows = WorkflowRepository(db)
        self.documents = DocumentRepository(db)
        self.assets = AssetRepository(db)
        self.qa_reports = QARepository(db)

    def create_project(self, payload: CreateProjectRequest) -> ProjectResponse:
        return _to_project_response(self.projects.create(payload))

    def list_projects(self) -> list[ProjectResponse]:
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
        return _to_workflow_response(self.workflows.create(project_id, episode_id, payload))

    def latest_workflow_for_episode(self, episode_id):
        return _to_workflow_response(self.workflows.latest_for_episode(episode_id))

    def build_workspace(self, project_id, episode_id) -> EpisodeWorkspaceResponse | None:
        project = self.get_project(project_id)
        episode = self.get_episode(episode_id)
        if not project or not episode:
            return None

        documents = [_to_document_summary(item) for item in self.documents.list_for_episode(episode_id)]
        assets = [_to_asset_summary(item) for item in self.assets.list_for_episode(episode_id)]
        qa_reports = [_to_qa_summary(item) for item in self.qa_reports.list_for_episode(episode_id)]

        qa_result = "pending"
        issue_count = 0
        if qa_reports:
            qa_result = qa_reports[0].result
            issue_count = sum(item.issue_count for item in qa_reports)

        return EpisodeWorkspaceResponse(
            project=project,
            episode=episode,
            documents=documents,
            shots=[
                ShotSummaryResponse(code="SHOT_01", duration_ms=6000, status="ready"),
                ShotSummaryResponse(code="SHOT_02", duration_ms=5000, status="ready"),
                ShotSummaryResponse(code="SHOT_03", duration_ms=7000, status="warning"),
            ],
            assets=assets,
            qa_summary=WorkspaceQAResponse(
                result=qa_result,
                issue_count=issue_count,
                reports=qa_reports,
            ),
            latest_workflow=self.latest_workflow_for_episode(episode_id),
            generated_at=datetime.now(UTC),
            metadata={"mode": "database-backed-workspace"},
        )
