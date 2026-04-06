from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AssetModel


class AssetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_episode(self, episode_id) -> List[AssetModel]:
        stmt = (
            select(AssetModel)
            .where(AssetModel.episode_id == episode_id)
            .order_by(AssetModel.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_selected_for_episode(self, episode_id) -> List[AssetModel]:
        stmt = (
            select(AssetModel)
            .where(
                AssetModel.episode_id == episode_id,
                AssetModel.is_selected.is_(True),
            )
            .order_by(AssetModel.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())
