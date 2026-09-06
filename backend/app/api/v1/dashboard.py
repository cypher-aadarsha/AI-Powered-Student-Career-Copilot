from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.career import CareerListItem
from app.schemas.dashboard import (
    ChecklistItem,
    DashboardData,
    DashboardResponse,
    InterviewStats,
    ProfileCompletion,
    ResumeSummary,
)
from app.schemas.job import JobListItem
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardResponse:
    result = DashboardService(db).get_dashboard(current_user.id)

    data = DashboardData(
        profile_completion=ProfileCompletion(
            score=result.profile_completion.score,
            checklist=[ChecklistItem(label=item.label, done=item.done) for item in result.profile_completion.checklist],
        ),
        latest_resume=(
            ResumeSummary(
                id=result.latest_resume.id,
                original_filename=result.latest_resume.original_filename,
                status=result.latest_resume.status,
                ai_score=result.latest_resume.ai_score,
                created_at=result.latest_resume.created_at,
            )
            if result.latest_resume
            else None
        ),
        top_career_matches=[
            CareerListItem(
                role=role,
                score=gap.score,
                matched_required=gap.total_required - len(gap.missing_required),
                total_required=gap.total_required,
                matched_preferred=gap.total_preferred - len(gap.missing_preferred),
                total_preferred=gap.total_preferred,
            )
            for role, gap in result.top_career_matches
        ],
        top_job_matches=[
            JobListItem(
                job=job,
                score=gap.score,
                matched_skills=gap.total_required - len(gap.missing_required),
                total_skills=gap.total_required,
            )
            for job, gap in result.top_job_matches
        ],
        skill_count=result.skill_count,
        interview_stats=InterviewStats(
            total_sessions=result.interview_stats.total_sessions,
            completed_sessions=result.interview_stats.completed_sessions,
            average_score=result.interview_stats.average_score,
        ),
        suggested_actions=result.suggested_actions,
    )
    return DashboardResponse(data=data)
