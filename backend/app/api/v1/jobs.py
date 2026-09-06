import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.job import JobDetail, JobDetailResponse, JobListItem, JobListResponse
from app.schemas.skill_match import MatchedSkill
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _service(db: Session) -> JobService:
    return JobService(db)


@router.get("", response_model=JobListResponse)
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> JobListResponse:
    ranked = _service(db).list_jobs_ranked(current_user.id)
    data = [
        JobListItem(
            job=job,
            score=gap.score,
            matched_skills=gap.total_required - len(gap.missing_required),
            total_skills=gap.total_required,
        )
        for job, gap in ranked
    ]
    return JobListResponse(data=data)


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDetailResponse:
    job, gap = _service(db).get_job_detail(current_user.id, job_id)
    detail = JobDetail(
        job=job,
        description=job.description,
        apply_url=job.apply_url,
        score=gap.score,
        matched_skills=[MatchedSkill(skill=skill, proficiency_level=level) for skill, level in gap.matched_skills],
        missing_skills=list(gap.missing_required),
        summary=gap.summary,
    )
    return JobDetailResponse(data=detail)
