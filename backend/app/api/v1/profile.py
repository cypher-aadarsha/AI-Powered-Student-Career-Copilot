import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import (
    CertificationResponse,
    CertificationWriteRequest,
    ExperienceResponse,
    ExperienceWriteRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    ProjectResponse,
    ProjectWriteRequest,
    SkillCreateRequest,
    StudentSkillResponse,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


def _service(db: Session) -> ProfileService:
    return ProfileService(db)


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProfileResponse:
    profile = _service(db).get_or_create_profile(current_user.id)
    db.commit()
    db.refresh(profile)
    return ProfileResponse(data=profile)


@router.put("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    profile = _service(db).update_profile(current_user.id, payload)
    db.commit()
    db.refresh(profile)
    return ProfileResponse(data=profile)


# --- skills -------------------------------------------------------------


@router.post("/skills", response_model=StudentSkillResponse, status_code=status.HTTP_201_CREATED)
def add_skill(
    payload: SkillCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentSkillResponse:
    student_skill = _service(db).add_skill(current_user.id, payload)
    db.commit()
    db.refresh(student_skill)
    return StudentSkillResponse(data=student_skill)


@router.delete("/skills/{student_skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(
    student_skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _service(db).remove_skill(current_user.id, student_skill_id)
    db.commit()


# --- projects -------------------------------------------------------------


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_project(
    payload: ProjectWriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = _service(db).add_project(current_user.id, payload)
    db.commit()
    db.refresh(project)
    return ProjectResponse(data=project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectWriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = _service(db).update_project(current_user.id, project_id, payload)
    db.commit()
    db.refresh(project)
    return ProjectResponse(data=project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _service(db).delete_project(current_user.id, project_id)
    db.commit()


# --- experiences ------------------------------------------------------------


@router.post("/experiences", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def add_experience(
    payload: ExperienceWriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExperienceResponse:
    experience = _service(db).add_experience(current_user.id, payload)
    db.commit()
    db.refresh(experience)
    return ExperienceResponse(data=experience)


@router.put("/experiences/{experience_id}", response_model=ExperienceResponse)
def update_experience(
    experience_id: uuid.UUID,
    payload: ExperienceWriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExperienceResponse:
    experience = _service(db).update_experience(current_user.id, experience_id, payload)
    db.commit()
    db.refresh(experience)
    return ExperienceResponse(data=experience)


@router.delete("/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _service(db).delete_experience(current_user.id, experience_id)
    db.commit()


# --- certifications ---------------------------------------------------------


@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def add_certification(
    payload: CertificationWriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CertificationResponse:
    certification = _service(db).add_certification(current_user.id, payload)
    db.commit()
    db.refresh(certification)
    return CertificationResponse(data=certification)


@router.put("/certifications/{certification_id}", response_model=CertificationResponse)
def update_certification(
    certification_id: uuid.UUID,
    payload: CertificationWriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CertificationResponse:
    certification = _service(db).update_certification(current_user.id, certification_id, payload)
    db.commit()
    db.refresh(certification)
    return CertificationResponse(data=certification)


@router.delete("/certifications/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(
    certification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _service(db).delete_certification(current_user.id, certification_id)
    db.commit()
