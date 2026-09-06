"""A curated career role and the skills it expects. This catalogue is
platform-curated (seeded via `seed/career_roles.py`), not student-authored —
there's no student-facing create/update here, only read + skill-gap
matching. Full admin CRUD for roles is Phase 10's job.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class RoleSkillImportance(str, enum.Enum):
    required = "required"
    preferred = "preferred"


class CareerRole(Base):
    __tablename__ = "career_roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skills: Mapped[list["CareerRoleSkill"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class CareerRoleSkill(Base):
    __tablename__ = "career_role_skills"
    __table_args__ = (UniqueConstraint("career_role_id", "skill_id", name="uq_career_role_skill"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )
    importance: Mapped[RoleSkillImportance] = mapped_column(
        Enum(RoleSkillImportance, name="role_skill_importance"), nullable=False
    )

    role: Mapped["CareerRole"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(lazy="joined")
