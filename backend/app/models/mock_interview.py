"""A student's mock interview session: a fixed set of assigned questions
(picked once at session start, see InterviewService._select_questions) plus
whatever answers they've submitted so far. Optionally scoped to a career
role so the technical questions lean toward that role's skills.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class SessionStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"


class MockInterviewSession(Base):
    __tablename__ = "mock_interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    career_role_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("career_roles.id", ondelete="SET NULL")
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"), nullable=False, default=SessionStatus.in_progress
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    profile: Mapped["StudentProfile"] = relationship(back_populates="mock_interview_sessions")
    career_role: Mapped["CareerRole | None"] = relationship()
    questions: Mapped[list["MockInterviewSessionQuestion"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="MockInterviewSessionQuestion.order_index"
    )
    answers: Mapped[list["MockInterviewAnswer"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="MockInterviewAnswer.created_at"
    )


class MockInterviewSessionQuestion(Base):
    """The fixed question set assigned to a session at start time — a join
    row so the same shared InterviewQuestion can appear in many sessions."""

    __tablename__ = "mock_interview_session_questions"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_question"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("interview_questions.id", ondelete="RESTRICT"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped["MockInterviewSession"] = relationship(back_populates="questions")
    question: Mapped["InterviewQuestion"] = relationship(lazy="joined")


class MockInterviewAnswer(Base):
    __tablename__ = "mock_interview_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_answer"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("interview_questions.id", ondelete="RESTRICT"), nullable=False
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_feedback: Mapped[list | None] = mapped_column(JSON)
    ai_score: Mapped[int | None] = mapped_column(Integer)
    ai_provider_used: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped["MockInterviewSession"] = relationship(back_populates="answers")
    question: Mapped["InterviewQuestion"] = relationship(lazy="joined")
