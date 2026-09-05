"""create student profile tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
        ),
        sa.Column("university", sa.String(length=255)),
        sa.Column("degree", sa.String(length=255)),
        sa.Column("semester", sa.Integer()),
        sa.Column("graduation_year", sa.Integer()),
        sa.Column("location", sa.String(length=255)),
        sa.Column("bio", sa.Text()),
        sa.Column("profile_picture_url", sa.String(length=1024)),
        sa.Column("github_url", sa.String(length=512)),
        sa.Column("linkedin_url", sa.String(length=512)),
        sa.Column("portfolio_url", sa.String(length=512)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "technical", "soft", "programming_language", "framework", "tool", name="skill_category"
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_skills_name_lower_unique", "skills", [sa.text("lower(name)")], unique=True)

    op.create_table(
        "student_skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "student_profile_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("student_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("skill_id", sa.Uuid(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.Column(
            "proficiency_level",
            sa.Enum("beginner", "intermediate", "advanced", "expert", name="proficiency_level"),
            nullable=False,
            server_default="beginner",
        ),
        sa.Column(
            "source",
            sa.Enum("manual", "resume_extracted", name="skill_source"),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("student_profile_id", "skill_id", name="uq_student_skill"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "student_profile_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("student_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("repo_url", sa.String(length=512)),
        sa.Column("demo_url", sa.String(length=512)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "project_skills",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("project_id", sa.Uuid(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Uuid(as_uuid=True), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),
    )

    op.create_table(
        "experiences",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "student_profile_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("student_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column(
            "employment_type",
            sa.Enum("internship", "part_time", "full_time", "freelance", "volunteer", name="employment_type"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "certifications",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "student_profile_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("student_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("issuer", sa.String(length=255)),
        sa.Column("issue_date", sa.Date()),
        sa.Column("credential_url", sa.String(length=512)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("certifications")
    op.drop_table("experiences")
    op.drop_table("project_skills")
    op.drop_table("projects")
    op.drop_table("student_skills")
    op.drop_index("ix_skills_name_lower_unique", table_name="skills")
    op.drop_table("skills")
    op.drop_table("student_profiles")

    sa.Enum(name="employment_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="skill_source").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="proficiency_level").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="skill_category").drop(op.get_bind(), checkfirst=True)
