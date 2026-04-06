from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProjectModel
from app.schemas.project import CreateProjectRequest


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: CreateProjectRequest) -> ProjectModel:
        project = ProjectModel(
            name=payload.name,
            source_mode=payload.source_mode,
            genre=payload.genre,
            target_platform=payload.target_platform,
            target_audience=payload.target_audience,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list(self) -> List[ProjectModel]:
        stmt = select(ProjectModel).order_by(ProjectModel.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get(self, project_id):
        return self.db.get(ProjectModel, project_id)
