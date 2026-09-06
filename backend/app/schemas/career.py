"""Request/response shapes for the career module (Phase 6). Every response
here is computed fresh per request against the current student's skills —
there's no stored "your score for role X" row, so it's always consistent
with the latest profile edit.
"""
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.student_skill import ProficiencyLevel
from app.schemas.profile import SkillPublic


class CareerRoleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None


class MatchedSkill(BaseModel):
    skill: SkillPublic
    proficiency_level: ProficiencyLevel


class CareerListItem(BaseModel):
    role: CareerRoleSummary
    score: int
    matched_required: int
    total_required: int
    matched_preferred: int
    total_preferred: int


class CareerListResponse(BaseModel):
    data: list[CareerListItem]


class CareerDetail(BaseModel):
    role: CareerRoleSummary
    score: int
    matched_skills: list[MatchedSkill]
    missing_required_skills: list[SkillPublic]
    missing_preferred_skills: list[SkillPublic]
    summary: str


class CareerDetailResponse(BaseModel):
    data: CareerDetail
