"""Auth guards shared by every protected router. Authorization is enforced
here, server-side, on every request — never inferred from what the frontend
chooses to render (TDD §18).
"""
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import InvalidTokenError, decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentication required.")

    settings = get_settings()
    try:
        payload = decode_access_token(
            credentials.credentials, secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
    except InvalidTokenError as exc:
        raise UnauthorizedError("Invalid or expired token.") from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Invalid or expired token.") from exc

    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Invalid or expired token.")
    return user


def require_role(*roles: UserRole):
    """Composable on top of get_current_user, e.g. Depends(require_role(UserRole.admin))."""

    def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("You do not have access to this resource.")
        return user

    return _dependency
