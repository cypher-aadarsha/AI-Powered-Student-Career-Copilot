import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import LearningResourceListResponse, LearningResourceResponse
from app.services.learning_service import LearningService

router = APIRouter(prefix="/learning-resources", tags=["learning"])


def _service(db: Session) -> LearningService:
    return LearningService(db)


@router.get("", response_model=LearningResourceListResponse)
def list_learning_resources(
    skill_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningResourceListResponse:
    resources = _service(db).list_resources(skill_id)
    return LearningResourceListResponse(data=resources)


@router.get("/{resource_id}", response_model=LearningResourceResponse)
def get_learning_resource(
    resource_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningResourceResponse:
    resource = _service(db).get_resource(resource_id)
    return LearningResourceResponse(data=resource)
