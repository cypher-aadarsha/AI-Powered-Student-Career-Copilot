"""Request/response shapes for the resume module (Phase 5). `raw_text` is
intentionally excluded from the public schema — it can be several KB and
the frontend only ever needs `parsed_data`'s summarized extraction plus the
AI fields.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.resume import ResumeStatus


class ResumePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    status: ResumeStatus
    parse_error: str | None
    parsed_data: dict | None
    ai_summary: str | None
    ai_strengths: list[str] | None
    ai_suggestions: list[str] | None
    ai_score: int | None
    ai_provider_used: str | None
    created_at: datetime
    updated_at: datetime


class ResumeResponse(BaseModel):
    data: ResumePublic


class ResumeListResponse(BaseModel):
    data: list[ResumePublic]
