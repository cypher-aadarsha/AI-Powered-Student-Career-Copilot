"""Request/response shapes for the admin panel (Phase 10). Every route that
uses these is guarded by require_role(UserRole.admin) at the router level
(app/api/v1/admin/__init__.py), so these schemas never need their own
ownership checks the way the student-facing ones do.

Skills on a write request are given by name + category (AdminSkillRef), the
same shape the student-facing "add skill" form already uses (see
schemas/profile.py's SkillCreateRequest) — resolved via
SkillRepository.get_or_create, not looked up by id. That lets an admin add
a brand-new skill to the catalogue while creating a role/job/resource/
question in one step, instead of needing a separate "manage skills" screen
first.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.interview_question import QuestionCategory, QuestionDifficulty
from app.models.job_posting import JobEmploymentType
from app.models.learning_resource import ResourceType
from app.models.skill import SkillCategory
from app.models.user import UserRole
from app.schemas.profile import SkillPublic


class AdminSkillRef(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: SkillCategory


# --- users -------------------------------------------------------------


class AdminUserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class AdminUserListResponse(BaseModel):
    data: list[AdminUserPublic]


class AdminUserResponse(BaseModel):
    data: AdminUserPublic


class AdminUserUpdateRequest(BaseModel):
    is_active: bool


# --- career roles -----------------------------------------------------------


class AdminCareerRoleWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    required_skills: list[AdminSkillRef] = Field(default_factory=list)
    preferred_skills: list[AdminSkillRef] = Field(default_factory=list)


class AdminCareerRolePublic(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    required_skills: list[SkillPublic]
    preferred_skills: list[SkillPublic]


class AdminCareerRoleListResponse(BaseModel):
    data: list[AdminCareerRolePublic]


class AdminCareerRoleResponse(BaseModel):
    data: AdminCareerRolePublic


# --- learning resources -----------------------------------------------------


class AdminLearningResourceWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    url: str = Field(min_length=1, max_length=1024)
    provider: str = Field(min_length=1, max_length=255)
    resource_type: ResourceType
    skills: list[AdminSkillRef] = Field(default_factory=list)


# Read responses for learning resources reuse LearningResourcePublic/
# LearningResourceListResponse/LearningResourceResponse from schemas/learning.py
# directly — the shape admins need (id, title, description, url, provider,
# resource_type, skills) is identical to what students already see, so a
# second copy of the same schema would only drift out of sync over time.


# --- job postings -----------------------------------------------------------


class AdminJobPostingWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    employment_type: JobEmploymentType
    is_remote: bool = False
    description: str | None = Field(default=None, max_length=4000)
    apply_url: str = Field(min_length=1, max_length=1024)
    skills: list[AdminSkillRef] = Field(default_factory=list)


class AdminJobPostingPublic(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    location: str
    employment_type: JobEmploymentType
    is_remote: bool
    description: str | None
    apply_url: str
    skills: list[SkillPublic]


class AdminJobPostingListResponse(BaseModel):
    data: list[AdminJobPostingPublic]


class AdminJobPostingResponse(BaseModel):
    data: AdminJobPostingPublic


# --- interview questions -----------------------------------------------------


class AdminInterviewQuestionWriteRequest(BaseModel):
    question_text: str = Field(min_length=1, max_length=2000)
    category: QuestionCategory
    difficulty: QuestionDifficulty
    model_answer: str | None = Field(default=None, max_length=2000)
    skills: list[AdminSkillRef] = Field(default_factory=list)


class AdminInterviewQuestionPublic(BaseModel):
    id: uuid.UUID
    question_text: str
    category: QuestionCategory
    difficulty: QuestionDifficulty
    model_answer: str | None
    skills: list[SkillPublic]


class AdminInterviewQuestionListResponse(BaseModel):
    data: list[AdminInterviewQuestionPublic]


class AdminInterviewQuestionResponse(BaseModel):
    data: AdminInterviewQuestionPublic
