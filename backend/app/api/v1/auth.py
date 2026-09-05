from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenData, TokenResponse, UserPublic, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    service = AuthService(db, get_settings())
    user = service.register(payload)
    db.commit()
    return UserResponse(data=UserPublic.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = AuthService(db, get_settings())
    token = service.authenticate(payload)
    return TokenResponse(data=TokenData(access_token=token))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> None:
    """JWTs are stateless: there is nothing to invalidate server-side in v1
    (see TDD §23 for the accepted trade-off). This endpoint exists so the
    client has a single place to call on sign-out and so the action is
    audit-loggable once a token blacklist is added."""
    return None
