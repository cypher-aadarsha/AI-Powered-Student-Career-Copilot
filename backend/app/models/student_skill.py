"""Join of a student profile to the skill catalogue, carrying the
per-student attributes (proficiency, how it got there) that don't belong on
either side of the join alone.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class ProficiencyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class SkillSource(str, enum.Enum):
    manual = "manual"
    resume_extracted = "resume_extracted"


class StudentSkill(Base):
    __tablename__ = "student_skills"
    __table_args__ = (UniqueConstraint("student_profile_id", "skill_id", name="uq_student_skill"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )
    proficiency_level: Mapped[ProficiencyLevel] = mapped_column(
        Enum(ProficiencyLevel, name="proficiency_level"), nullable=False, default=ProficiencyLevel.beginner
    )
    source: Mapped[SkillSource] = mapped_column(
        Enum(SkillSource, name="skill_source"), nullable=False, default=SkillSource.manual
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    profile: Mapped["StudentProfile"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(lazy="joined")
