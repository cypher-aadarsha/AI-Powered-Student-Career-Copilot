import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job_posting import JobPosting
from app.schemas.admin import AdminJobPostingListResponse, AdminJobPostingPublic, AdminJobPostingResponse, AdminJobPostingWriteRequest
from app.services.admin_service import AdminService

router = APIRouter(prefix="/job-postings")


def _to_public(job: JobPosting) -> AdminJobPostingPublic:
    return AdminJobPostingPublic(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        employment_type=job.employment_type,
        is_remote=job.is_remote,
        description=job.description,
        apply_url=job.apply_url,
        skills=[js.skill for js in job.skills],
    )


@router.get("", response_model=AdminJobPostingListResponse)
def list_job_postings(db: Session = Depends(get_db)) -> AdminJobPostingListResponse:
    jobs = AdminService(db).list_job_postings()
    return AdminJobPostingListResponse(data=[_to_public(job) for job in jobs])


@router.post("", response_model=AdminJobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(payload: AdminJobPostingWriteRequest, db: Session = Depends(get_db)) -> AdminJobPostingResponse:
    job = AdminService(db).create_job_posting(payload)
    db.commit()
    db.refresh(job)
    return AdminJobPostingResponse(data=_to_public(job))


@router.put("/{job_id}", response_model=AdminJobPostingResponse)
def update_job_posting(
    job_id: uuid.UUID, payload: AdminJobPostingWriteRequest, db: Session = Depends(get_db)
) -> AdminJobPostingResponse:
    job = AdminService(db).update_job_posting(job_id, payload)
    db.commit()
    db.refresh(job)
    return AdminJobPostingResponse(data=_to_public(job))


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(job_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    AdminService(db).delete_job_posting(job_id)
    db.commit()
