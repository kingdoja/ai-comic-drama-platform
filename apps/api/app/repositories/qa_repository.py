from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import QAReportModel


class QARepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_episode(self, episode_id) -> list[QAReportModel]:
        stmt = (
            select(QAReportModel)
            .where(QAReportModel.episode_id == episode_id)
            .order_by(QAReportModel.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())
