"""The interview question bank. Platform-curated like career_role.py and
learning_resource.py — seeded via `seed/interview_questions.py`, not
student-authored. Behavioral/situational questions are typically untagged
(general); technical questions are tagged with the skills they probe so a
mock interview session can pull role-relevant ones.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class QuestionCategory(str, enum.Enum):
    behavioral = "behavioral"
    technical = "technical"
    situational = "situational"


class QuestionDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[QuestionCategory] = mapped_column(Enum(QuestionCategory, name="question_category"), nullable=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        Enum(QuestionDifficulty, name="question_difficulty"), nullable=False
    )
    # Guidance text for the heuristic feedback provider to compare an answer
    # against (keyword overlap) — never shown to the student before they answer.
    model_answer: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skills: Mapped[list["InterviewQuestionSkill"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class InterviewQuestionSkill(Base):
    __tablename__ = "interview_question_skills"
    __table_args__ = (UniqueConstraint("interview_question_id", "skill_id", name="uq_interview_question_skill"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )

    question: Mapped["InterviewQuestion"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(lazy="joined")
