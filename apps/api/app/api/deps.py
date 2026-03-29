from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.store import DatabaseStore


def get_store(db: Session = Depends(get_db)) -> DatabaseStore:
    return DatabaseStore(db)
