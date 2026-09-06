import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_posting import JobPosting


class JobPostingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[JobPosting]:
        stmt = select(JobPosting).order_by(JobPosting.title)
        return list(self.db.scalars(stmt))

    def get_by_id(self, job_id: uuid.UUID) -> JobPosting | None:
        return self.db.get(JobPosting, job_id)
