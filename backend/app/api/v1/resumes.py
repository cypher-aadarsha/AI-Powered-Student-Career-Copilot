import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.resume import ResumeListResponse, ResumeResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _service(db: Session) -> ResumeService:
    return ResumeService(db)


@router.get("", response_model=ResumeListResponse)
def list_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ResumeListResponse:
    resumes = _service(db).list_resumes(current_user.id)
    return ResumeListResponse(data=resumes)


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    resume = _service(db).upload_resume(current_user.id, file)
    db.commit()
    db.refresh(resume)
    return ResumeResponse(data=resume)


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    resume = _service(db).get_resume(current_user.id, resume_id)
    return ResumeResponse(data=resume)


@router.post("/{resume_id}/reanalyze", response_model=ResumeResponse)
def reanalyze_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    resume = _service(db).reanalyze_resume(current_user.id, resume_id)
    db.commit()
    db.refresh(resume)
    return ResumeResponse(data=resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _service(db).delete_resume(current_user.id, resume_id)
    db.commit()
