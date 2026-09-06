import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_posting import JobEmploymentType, JobPosting, JobPostingSkill


class JobPostingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[JobPosting]:
        stmt = select(JobPosting).order_by(JobPosting.title)
        return list(self.db.scalars(stmt))

    def get_by_id(self, job_id: uuid.UUID) -> JobPosting | None:
        return self.db.get(JobPosting, job_id)

    def create(
        self,
        *,
        title: str,
        company: str,
        location: str,
        employment_type: JobEmploymentType,
        is_remote: bool,
        description: str | None,
        apply_url: str,
    ) -> JobPosting:
        job = JobPosting(
            title=title,
            company=company,
            location=location,
            employment_type=employment_type,
            is_remote=is_remote,
            description=description,
            apply_url=apply_url,
        )
        self.db.add(job)
        self.db.flush()
        return job

    def update(
        self,
        job: JobPosting,
        *,
        title: str,
        company: str,
        location: str,
        employment_type: JobEmploymentType,
        is_remote: bool,
        description: str | None,
        apply_url: str,
    ) -> JobPosting:
        job.title = title
        job.company = company
        job.location = location
        job.employment_type = employment_type
        job.is_remote = is_remote
        job.description = description
        job.apply_url = apply_url
        self.db.flush()
        return job

    def delete(self, job: JobPosting) -> None:
        self.db.delete(job)

    def set_skills(self, job: JobPosting, skill_ids: list[uuid.UUID]) -> None:
        for existing in list(job.skills):
            self.db.delete(existing)
        self.db.flush()
        for skill_id in dict.fromkeys(skill_ids):
            self.db.add(JobPostingSkill(job_posting_id=job.id, skill_id=skill_id))
        self.db.flush()
