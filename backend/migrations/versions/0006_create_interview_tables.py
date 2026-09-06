"""create interview question and mock interview tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_questions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column(
            "category",
            sa.Enum("behavioral", "technical", "situational", name="question_category"),
            nullable=False,
        ),
        sa.Column("difficulty", sa.Enum("easy", "medium", "hard", name="question_difficulty"), nullable=False),
        sa.Column("model_answer", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "interview_question_skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "interview_question_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("interview_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("skill_id", sa.Uuid(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("interview_question_id", "skill_id", name="uq_interview_question_skill"),
    )

    op.create_table(
        "mock_interview_sessions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "student_profile_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("student_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("career_role_id", sa.Uuid(as_uuid=True), sa.ForeignKey("career_roles.id", ondelete="SET NULL")),
        sa.Column(
            "status",
            sa.Enum("in_progress", "completed", name="session_status"),
            nullable=False,
            server_default="in_progress",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_mock_interview_sessions_student_profile_id", "mock_interview_sessions", ["student_profile_id"])

    op.create_table(
        "mock_interview_session_questions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id", sa.Uuid(as_uuid=True), sa.ForeignKey("interview_questions.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.UniqueConstraint("session_id", "question_id", name="uq_session_question"),
    )

    op.create_table(
        "mock_interview_answers",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id", sa.Uuid(as_uuid=True), sa.ForeignKey("interview_questions.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("ai_feedback", sa.JSON()),
        sa.Column("ai_score", sa.Integer()),
        sa.Column("ai_provider_used", sa.String(length=20)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("session_id", "question_id", name="uq_session_answer"),
    )


def downgrade() -> None:
    op.drop_table("mock_interview_answers")
    op.drop_table("mock_interview_session_questions")
    op.drop_index("ix_mock_interview_sessions_student_profile_id", table_name="mock_interview_sessions")
    op.drop_table("mock_interview_sessions")
    op.drop_table("interview_question_skills")
    op.drop_table("interview_questions")

    sa.Enum(name="session_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="question_difficulty").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="question_category").drop(op.get_bind(), checkfirst=True)
