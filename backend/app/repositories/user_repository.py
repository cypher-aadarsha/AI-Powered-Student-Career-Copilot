"""Query object for the `users` table — the only place that writes raw
SQLAlchemy queries against User; services never touch the session directly.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def create(self, *, email: str, password_hash: str, full_name: str, role: UserRole = UserRole.student) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name, role=role)
        self.db.add(user)
        self.db.flush()
        return user
