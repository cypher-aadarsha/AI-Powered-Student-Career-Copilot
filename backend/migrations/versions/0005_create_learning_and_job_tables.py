"""create learning resource and job posting tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=False),
        sa.Column(
            "resource_type",
            sa.Enum("course", "tutorial", "article", "video", "book", "documentation", name="resource_type"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "learning_resource_skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "learning_resource_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("learning_resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("skill_id", sa.Uuid(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("learning_resource_id", "skill_id", name="uq_learning_resource_skill"),
    )

    op.create_table(
        "job_postings",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column(
            "employment_type",
            sa.Enum("full_time", "part_time", "internship", "contract", name="job_employment_type"),
            nullable=False,
        ),
        sa.Column("is_remote", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("description", sa.Text()),
        sa.Column("apply_url", sa.String(length=1024), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "job_posting_skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "job_posting_id", sa.Uuid(as_uuid=True), sa.ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("skill_id", sa.Uuid(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("job_posting_id", "skill_id", name="uq_job_posting_skill"),
    )


def downgrade() -> None:
    op.drop_table("job_posting_skills")
    op.drop_table("job_postings")
    op.drop_table("learning_resource_skills")
    op.drop_table("learning_resources")

    sa.Enum(name="job_employment_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="resource_type").drop(op.get_bind(), checkfirst=True)
