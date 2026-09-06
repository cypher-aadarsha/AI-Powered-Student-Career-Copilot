"""A curated learning resource (course, article, docs, etc.) tagged with
the skills it teaches. Platform-curated like career_role.py — seeded via
`seed/learning_resources.py`, not student-authored.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class ResourceType(str, enum.Enum):
    course = "course"
    tutorial = "tutorial"
    article = "article"
    video = "video"
    book = "book"
    documentation = "documentation"


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType, name="resource_type"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skills: Mapped[list["LearningResourceSkill"]] = relationship(
        back_populates="resource", cascade="all, delete-orphan"
    )


class LearningResourceSkill(Base):
    __tablename__ = "learning_resource_skills"
    __table_args__ = (UniqueConstraint("learning_resource_id", "skill_id", name="uq_learning_resource_skill"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )

    resource: Mapped["LearningResource"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(lazy="joined")
