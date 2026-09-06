"""Request/response shapes for the career dashboard (Phase 9). Top career
and job matches reuse CareerListItem/JobListItem — the exact shape their
own list endpoints return — so the frontend doesn't need a second type for
"the same card, but on the dashboard."
"""
import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.resume import ResumeStatus
from app.schemas.career import CareerListItem
from app.schemas.job import JobListItem


class ChecklistItem(BaseModel):
    label: str
    done: bool


class ProfileCompletion(BaseModel):
    score: int
    checklist: list[ChecklistItem]


class ResumeSummary(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: ResumeStatus
    ai_score: int | None
    created_at: datetime


class InterviewStats(BaseModel):
    total_sessions: int
    completed_sessions: int
    average_score: int | None


class DashboardData(BaseModel):
    profile_completion: ProfileCompletion
    latest_resume: ResumeSummary | None
    top_career_matches: list[CareerListItem]
    top_job_matches: list[JobListItem]
    skill_count: int
    interview_stats: InterviewStats
    suggested_actions: list[str]


class DashboardResponse(BaseModel):
    data: DashboardData
