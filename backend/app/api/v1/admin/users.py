import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminUserListResponse, AdminUserResponse, AdminUserUpdateRequest
from app.services.admin_service import AdminService

router = APIRouter(prefix="/users")


@router.get("", response_model=AdminUserListResponse)
def list_users(db: Session = Depends(get_db)) -> AdminUserListResponse:
    users = AdminService(db).list_users()
    return AdminUserListResponse(data=users)


@router.patch("/{user_id}", response_model=AdminUserResponse)
def update_user_status(
    user_id: uuid.UUID,
    payload: AdminUserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    user = AdminService(db).set_user_active(current_user.id, user_id, payload.is_active)
    db.commit()
    db.refresh(user)
    return AdminUserResponse(data=user)
