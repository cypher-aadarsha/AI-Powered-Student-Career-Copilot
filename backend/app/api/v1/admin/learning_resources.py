import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.admin import AdminLearningResourceWriteRequest
from app.schemas.learning import LearningResourceListResponse, LearningResourceResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/learning-resources")


@router.get("", response_model=LearningResourceListResponse)
def list_learning_resources(db: Session = Depends(get_db)) -> LearningResourceListResponse:
    resources = AdminService(db).list_learning_resources()
    return LearningResourceListResponse(data=resources)


@router.post("", response_model=LearningResourceResponse, status_code=status.HTTP_201_CREATED)
def create_learning_resource(
    payload: AdminLearningResourceWriteRequest, db: Session = Depends(get_db)
) -> LearningResourceResponse:
    resource = AdminService(db).create_learning_resource(payload)
    db.commit()
    db.refresh(resource)
    return LearningResourceResponse(data=resource)


@router.put("/{resource_id}", response_model=LearningResourceResponse)
def update_learning_resource(
    resource_id: uuid.UUID, payload: AdminLearningResourceWriteRequest, db: Session = Depends(get_db)
) -> LearningResourceResponse:
    resource = AdminService(db).update_learning_resource(resource_id, payload)
    db.commit()
    db.refresh(resource)
    return LearningResourceResponse(data=resource)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_resource(resource_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    AdminService(db).delete_learning_resource(resource_id)
    db.commit()
