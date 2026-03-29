from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DocumentModel


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_episode(self, episode_id) -> list[DocumentModel]:
        stmt = (
            select(DocumentModel)
            .where(DocumentModel.episode_id == episode_id)
            .order_by(DocumentModel.updated_at.desc())
        )
        return list(self.db.scalars(stmt).all())
