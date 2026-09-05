import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> StudentProfile | None:
        return self.db.scalar(select(StudentProfile).where(StudentProfile.user_id == user_id))

    def create(self, *, user_id: uuid.UUID) -> StudentProfile:
        profile = StudentProfile(user_id=user_id)
        self.db.add(profile)
        self.db.flush()
        return profile
