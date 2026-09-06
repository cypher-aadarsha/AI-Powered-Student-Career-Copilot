import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume import Resume, ResumeStatus


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_profile(self, student_profile_id: uuid.UUID) -> list[Resume]:
        stmt = select(Resume).where(Resume.student_profile_id == student_profile_id).order_by(Resume.created_at.desc())
        return list(self.db.scalars(stmt))

    def get_by_id(self, resume_id: uuid.UUID) -> Resume | None:
        return self.db.get(Resume, resume_id)

    def create(
        self,
        *,
        student_profile_id: uuid.UUID,
        original_filename: str,
        storage_path: str,
        mime_type: str,
        file_size_bytes: int,
    ) -> Resume:
        resume = Resume(
            student_profile_id=student_profile_id,
            original_filename=original_filename,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            status=ResumeStatus.uploaded,
        )
        self.db.add(resume)
        self.db.flush()
        return resume

    def delete(self, resume: Resume) -> None:
        self.db.delete(resume)
