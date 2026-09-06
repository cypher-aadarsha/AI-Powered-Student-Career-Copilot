"""create career role tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "career_roles",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "career_role_skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "career_role_id", sa.Uuid(as_uuid=True), sa.ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("skill_id", sa.Uuid(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.Column(
            "importance",
            sa.Enum("required", "preferred", name="role_skill_importance"),
            nullable=False,
        ),
        sa.UniqueConstraint("career_role_id", "skill_id", name="uq_career_role_skill"),
    )


def downgrade() -> None:
    op.drop_table("career_role_skills")
    op.drop_table("career_roles")
    sa.Enum(name="role_skill_importance").drop(op.get_bind(), checkfirst=True)
