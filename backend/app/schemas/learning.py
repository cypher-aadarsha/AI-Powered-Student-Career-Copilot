"""Request/response shapes for the learning-resources module (Phase 7)."""
import uuid

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.learning_resource import ResourceType
from app.schemas.career import CareerRoleSummary
from app.schemas.profile import SkillPublic


class LearningResourcePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None
    url: str
    provider: str
    resource_type: ResourceType
    skills: list[SkillPublic]

    @field_validator("skills", mode="before")
    @classmethod
    def _unwrap_resource_skills(cls, value):
        # LearningResource.skills is a list of LearningResourceSkill join
        # rows; unwrap to the underlying Skill, same pattern as
        # ProjectPublic._unwrap_project_skills in schemas/profile.py.
        return [item.skill if hasattr(item, "skill") else item for item in value]


class LearningResourceListResponse(BaseModel):
    data: list[LearningResourcePublic]


class LearningResourceResponse(BaseModel):
    data: LearningResourcePublic


class SkillWithResources(BaseModel):
    skill: SkillPublic
    resources: list[LearningResourcePublic]


class RoleLearningPlan(BaseModel):
    role: CareerRoleSummary
    missing_required: list[SkillWithResources]
    missing_preferred: list[SkillWithResources]


class RoleLearningPlanResponse(BaseModel):
    data: RoleLearningPlan
