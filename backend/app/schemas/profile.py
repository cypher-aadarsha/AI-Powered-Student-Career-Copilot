"""Request/response shapes for the profile module (Phase 4).

Every nested list on ProfilePublic mirrors a real relational table (TDD §8)
— skills, projects, experiences, certifications are never a JSON blob.
"""
import uuid
from datetime import date, datetime

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, field_validator

from app.models.experience import EmploymentType
from app.models.skill import SkillCategory
from app.models.student_skill import ProficiencyLevel, SkillSource


def _validate_optional_url(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    AnyUrl(value)  # raises pydantic_core.ValidationError-compatible error if malformed
    return value


class ProfileUpdateRequest(BaseModel):
    university: str | None = Field(default=None, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    semester: int | None = Field(default=None, ge=1, le=12)
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    location: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    profile_picture_url: str | None = Field(default=None, max_length=1024)
    github_url: str | None = Field(default=None, max_length=512)
    linkedin_url: str | None = Field(default=None, max_length=512)
    portfolio_url: str | None = Field(default=None, max_length=512)

    _validate_urls = field_validator(
        "profile_picture_url", "github_url", "linkedin_url", "portfolio_url"
    )(_validate_optional_url)


# --- Skills -------------------------------------------------------------


class SkillCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: SkillCategory
    proficiency_level: ProficiencyLevel = ProficiencyLevel.beginner


class SkillPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    category: SkillCategory


class StudentSkillPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    proficiency_level: ProficiencyLevel
    source: SkillSource
    skill: SkillPublic


class StudentSkillResponse(BaseModel):
    data: StudentSkillPublic


# --- Projects -------------------------------------------------------------


class ProjectWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    repo_url: str | None = Field(default=None, max_length=512)
    demo_url: str | None = Field(default=None, max_length=512)
    start_date: date | None = None
    end_date: date | None = None
    skill_ids: list[uuid.UUID] = Field(default_factory=list)

    _validate_urls = field_validator("repo_url", "demo_url")(_validate_optional_url)

    @field_validator("end_date")
    @classmethod
    def _end_after_start(cls, end_date: date | None, info) -> date | None:
        start_date = info.data.get("start_date")
        if end_date and start_date and end_date < start_date:
            raise ValueError("end_date cannot be before start_date")
        return end_date


class ProjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None
    repo_url: str | None
    demo_url: str | None
    start_date: date | None
    end_date: date | None
    skills: list[SkillPublic]
    created_at: datetime
    updated_at: datetime

    @field_validator("skills", mode="before")
    @classmethod
    def _unwrap_project_skills(cls, value):
        # `Project.skills` is a list of ProjectSkill join rows; unwrap to the
        # underlying Skill so the API returns skills directly, not the join.
        return [item.skill if hasattr(item, "skill") else item for item in value]


class ProjectResponse(BaseModel):
    data: ProjectPublic


# --- Experiences ------------------------------------------------------------


class ExperienceWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    employment_type: EmploymentType
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    description: str | None = Field(default=None, max_length=4000)

    @field_validator("end_date")
    @classmethod
    def _end_after_start(cls, end_date: date | None, info) -> date | None:
        start_date = info.data.get("start_date")
        if end_date and start_date and end_date < start_date:
            raise ValueError("end_date cannot be before start_date")
        return end_date


class ExperiencePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    company: str
    employment_type: EmploymentType
    start_date: date
    end_date: date | None
    is_current: bool
    description: str | None
    created_at: datetime
    updated_at: datetime


class ExperienceResponse(BaseModel):
    data: ExperiencePublic


# --- Certifications ---------------------------------------------------------


class CertificationWriteRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    issuer: str | None = Field(default=None, max_length=255)
    issue_date: date | None = None
    credential_url: str | None = Field(default=None, max_length=512)

    _validate_urls = field_validator("credential_url")(_validate_optional_url)


class CertificationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    issuer: str | None
    issue_date: date | None
    credential_url: str | None
    created_at: datetime
    updated_at: datetime


class CertificationResponse(BaseModel):
    data: CertificationPublic


# --- Profile (aggregate) -----------------------------------------------------


class ProfilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    university: str | None
    degree: str | None
    semester: int | None
    graduation_year: int | None
    location: str | None
    bio: str | None
    profile_picture_url: str | None
    github_url: str | None
    linkedin_url: str | None
    portfolio_url: str | None
    skills: list[StudentSkillPublic]
    projects: list[ProjectPublic]
    experiences: list[ExperiencePublic]
    certifications: list[CertificationPublic]
    created_at: datetime
    updated_at: datetime


class ProfileResponse(BaseModel):
    data: ProfilePublic
