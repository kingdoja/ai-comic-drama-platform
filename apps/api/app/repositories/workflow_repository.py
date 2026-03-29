import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import WorkflowRunModel
from app.schemas.workflow import StartEpisodeWorkflowRequest


class WorkflowRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, project_id, episode_id, payload: StartEpisodeWorkflowRequest) -> WorkflowRunModel:
        workflow = WorkflowRunModel(
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind=payload.start_stage,
            temporal_workflow_id=f"episode-{episode_id}-{uuid.uuid4()}",
            temporal_run_id=str(uuid.uuid4()),
            status="running",
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def latest_for_episode(self, episode_id):
        stmt = (
            select(WorkflowRunModel)
            .where(WorkflowRunModel.episode_id == episode_id)
            .order_by(WorkflowRunModel.started_at.desc())
        )
        return self.db.scalars(stmt).first()
