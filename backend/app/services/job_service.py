"""Job-posting browsing + skill matching (Phase 7). Same shape as
CareerService (Phase 6): job postings are shared platform data (seeded via
`seed/job_postings.py`, not student-authored), and the match score is
computed fresh from the student's current skills on every request.

A job's skill list has no required/preferred split — every skill it lists
is passed to `compute_skill_gap` as "required" and preferred is left empty,
reusing the exact same explainable weighted-proficiency formula the career
module uses rather than inventing a second scoring rule.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.job_posting import JobPosting
from app.repositories.job_posting_repository import JobPostingRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.skill_gap import SkillGapResult, compute_skill_gap, student_skill_levels


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.profiles = ProfileRepository(db)
        self.jobs = JobPostingRepository(db)

    def list_jobs_ranked(self, user_id: uuid.UUID) -> list[tuple[JobPosting, SkillGapResult]]:
        student_skills = student_skill_levels(self.profiles.get_by_user_id(user_id))
        results = [(job, self._gap_for_job(job, student_skills)) for job in self.jobs.list_all()]
        results.sort(key=lambda pair: pair[1].score, reverse=True)
        return results

    def get_job_detail(self, user_id: uuid.UUID, job_id: uuid.UUID) -> tuple[JobPosting, SkillGapResult]:
        job = self.jobs.get_by_id(job_id)
        if job is None:
            raise NotFoundError("Job posting not found.")
        student_skills = student_skill_levels(self.profiles.get_by_user_id(user_id))
        return job, self._gap_for_job(job, student_skills)

    def _gap_for_job(self, job: JobPosting, student_skills: dict) -> SkillGapResult:
        required = [js.skill for js in job.skills]
        return compute_skill_gap(student_skills, required, [])
