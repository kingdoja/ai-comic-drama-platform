from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class Meta(BaseModel):
    request_id: str = Field(default="dev-request")


class SuccessEnvelope(BaseModel):
    data: Any
    meta: Meta = Field(default_factory=Meta)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    error: ErrorBody
    meta: Meta = Field(default_factory=Meta)


class Timestamps(BaseModel):
    created_at: datetime
    updated_at: datetime


class IdMixin(BaseModel):
    id: UUID
