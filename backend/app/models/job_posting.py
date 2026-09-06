"""A job posting and the skills it requires. Platform-curated demo data
(seeded via `seed/job_postings.py`, fictional companies) — this phase
matches a student's skills against postings, it doesn't ingest a live job
board. Reuses the same required-skill shape as career_role.py, but flat
(no required/preferred split): a job's skill match reuses
`skill_gap.compute_skill_gap` with every job skill passed as "required".
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class JobEmploymentType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    internship = "internship"
    contract = "contract"


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    employment_type: Mapped[JobEmploymentType] = mapped_column(
        Enum(JobEmploymentType, name="job_employment_type"), nullable=False
    )
    is_remote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    apply_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skills: Mapped[list["JobPostingSkill"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobPostingSkill(Base):
    __tablename__ = "job_posting_skills"
    __table_args__ = (UniqueConstraint("job_posting_id", "skill_id", name="uq_job_posting_skill"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_posting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )

    job: Mapped["JobPosting"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(lazy="joined")
