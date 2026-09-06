"""create resumes table

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resumes",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "student_profile_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("student_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("uploaded", "parsing", "parsed", "failed", name="resume_status"),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column("parse_error", sa.Text()),
        sa.Column("raw_text", sa.Text()),
        sa.Column("parsed_data", sa.JSON()),
        sa.Column("ai_summary", sa.Text()),
        sa.Column("ai_strengths", sa.JSON()),
        sa.Column("ai_suggestions", sa.JSON()),
        sa.Column("ai_score", sa.Integer()),
        sa.Column("ai_provider_used", sa.String(length=20)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_resumes_student_profile_id", "resumes", ["student_profile_id"])


def downgrade() -> None:
    op.drop_index("ix_resumes_student_profile_id", table_name="resumes")
    op.drop_table("resumes")
    sa.Enum(name="resume_status").drop(op.get_bind(), checkfirst=True)
