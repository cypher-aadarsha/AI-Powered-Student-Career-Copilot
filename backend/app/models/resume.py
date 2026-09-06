"""A student's uploaded resume: the stored file plus everything extracted
and inferred from it. A profile can hold several resumes (re-uploads keep
history instead of overwriting) — callers that want "the current one" take
the most recently created row; there is no separate is_active flag to keep
in sync with that ordering.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class ResumeStatus(str, enum.Enum):
    uploaded = "uploaded"
    parsing = "parsing"
    parsed = "parsed"
    failed = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[ResumeStatus] = mapped_column(
        Enum(ResumeStatus, name="resume_status"), nullable=False, default=ResumeStatus.uploaded
    )
    parse_error: Mapped[str | None] = mapped_column(Text)

    # Parsing output (PyMuPDF/pdfplumber or python-docx, depending on file type)
    raw_text: Mapped[str | None] = mapped_column(Text)
    parsed_data: Mapped[dict | None] = mapped_column(JSON)

    # AI analysis output (app/ai — provider-agnostic, see ai/provider.py)
    ai_summary: Mapped[str | None] = mapped_column(Text)
    ai_strengths: Mapped[list | None] = mapped_column(JSON)
    ai_suggestions: Mapped[list | None] = mapped_column(JSON)
    ai_score: Mapped[int | None] = mapped_column(Integer)
    ai_provider_used: Mapped[str | None] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profile: Mapped["StudentProfile"] = relationship(back_populates="resumes")
