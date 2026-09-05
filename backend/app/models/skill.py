"""The canonical skill catalogue — every other table (student_skills,
project_skills, and later career_role_skills / job_skills) references a row
here instead of storing free text, which is what makes matching algorithms
(Phase 6) a real join instead of fuzzy string comparison.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base


class SkillCategory(str, enum.Enum):
    technical = "technical"
    soft = "soft"
    programming_language = "programming_language"
    framework = "framework"
    tool = "tool"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory, name="skill_category"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        # Case-insensitive uniqueness: "React" and "react" are the same skill.
        Index("ix_skills_name_lower_unique", func.lower(name), unique=True),
    )
