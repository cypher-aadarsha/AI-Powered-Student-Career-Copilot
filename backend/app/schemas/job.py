"""Request/response shapes for the job-matching module (Phase 7). Scores
are computed fresh per request, same as the career module — see
app/services/job_service.py for how a job's flat skill list reuses
skill_gap.compute_skill_gap with everything passed as "required".
"""
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.job_posting import JobEmploymentType
from app.schemas.profile import SkillPublic
from app.schemas.skill_match import MatchedSkill


class JobPostingSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    company: str
    location: str
    employment_type: JobEmploymentType
    is_remote: bool


class JobListItem(BaseModel):
    job: JobPostingSummary
    score: int
    matched_skills: int
    total_skills: int


class JobListResponse(BaseModel):
    data: list[JobListItem]


class JobDetail(BaseModel):
    job: JobPostingSummary
    description: str | None
    apply_url: str
    score: int
    matched_skills: list[MatchedSkill]
    missing_skills: list[SkillPublic]
    summary: str


class JobDetailResponse(BaseModel):
    data: JobDetail
