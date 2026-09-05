"""Registration and login business logic. Routers never hash a password,
verify one, or mint a token directly — it all funnels through here so the
rules (and the audit log) live in exactly one place.
"""
import logging

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session, settings: Settings):
        self.repo = UserRepository(db)
        self.settings = settings

    def register(self, data: RegisterRequest) -> User:
        """Self-registration always creates a `student` account — admin
        accounts are provisioned out-of-band (seed data / an existing admin),
        never chosen by the registering user."""
        if self.repo.get_by_email(data.email):
            raise ConflictError("An account with this email already exists.")

        user = self.repo.create(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
        )
        logger.info("user_registered user_id=%s role=%s", user.id, user.role.value)
        return user

    def authenticate(self, data: LoginRequest) -> str:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning("login_failed")
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise ForbiddenError("This account has been disabled.")

        logger.info("login_succeeded user_id=%s", user.id)
        return create_access_token(
            subject=str(user.id),
            role=user.role.value,
            secret_key=self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
            expires_minutes=self.settings.access_token_expire_minutes,
        )
