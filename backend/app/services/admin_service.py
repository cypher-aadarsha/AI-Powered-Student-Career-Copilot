"""Admin panel business logic (Phase 10): user moderation plus full CRUD
for the four platform-curated catalogues (career roles, learning resources,
job postings, interview questions) that every earlier phase deliberately
left read-only on the student-facing side. One service composing the
existing repositories, the same shape as LearningService composing
CareerService — nothing here duplicates logic those repositories already
have.
"""
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.models.career_role import CareerRole
from app.models.interview_question import InterviewQuestion
from app.models.job_posting import JobPosting
from app.models.learning_resource import LearningResource
from app.models.skill import Skill
from app.models.user import User
from app.repositories.career_role_repository import CareerRoleRepository
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.repositories.learning_resource_repository import LearningResourceRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import (
    AdminCareerRoleWriteRequest,
    AdminInterviewQuestionWriteRequest,
    AdminJobPostingWriteRequest,
    AdminLearningResourceWriteRequest,
    AdminSkillRef,
)


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.skills = SkillRepository(db)
        self.career_roles = CareerRoleRepository(db)
        self.learning_resources = LearningResourceRepository(db)
        self.job_postings = JobPostingRepository(db)
        self.interview_questions = InterviewQuestionRepository(db)

    # --- users -----------------------------------------------------------

    def list_users(self) -> list[User]:
        return self.users.list_all()

    def set_user_active(self, acting_admin_id: uuid.UUID, target_user_id: uuid.UUID, is_active: bool) -> User:
        if target_user_id == acting_admin_id and not is_active:
            raise AppError("You can't deactivate your own account.", status_code=400, code="cannot_deactivate_self")
        user = self.users.get_by_id(target_user_id)
        if user is None:
            raise NotFoundError("User not found.")
        user.is_active = is_active
        self.db.flush()
        return user

    # --- career roles ------------------------------------------------------

    def list_career_roles(self) -> list[CareerRole]:
        return self.career_roles.list_all()

    def create_career_role(self, data: AdminCareerRoleWriteRequest) -> CareerRole:
        if self.career_roles.get_by_title(data.title) is not None:
            raise ConflictError(f'A career role titled "{data.title}" already exists.')
        role = self.career_roles.create(title=data.title, description=data.description)
        self._apply_career_role_skills(role, data)
        return role

    def update_career_role(self, role_id: uuid.UUID, data: AdminCareerRoleWriteRequest) -> CareerRole:
        role = self.career_roles.get_by_id(role_id)
        if role is None:
            raise NotFoundError("Career role not found.")
        existing = self.career_roles.get_by_title(data.title)
        if existing is not None and existing.id != role.id:
            raise ConflictError(f'A career role titled "{data.title}" already exists.')
        self.career_roles.update(role, title=data.title, description=data.description)
        self._apply_career_role_skills(role, data)
        return role

    def delete_career_role(self, role_id: uuid.UUID) -> None:
        role = self.career_roles.get_by_id(role_id)
        if role is None:
            raise NotFoundError("Career role not found.")
        self.career_roles.delete(role)

    def _apply_career_role_skills(self, role: CareerRole, data: AdminCareerRoleWriteRequest) -> None:
        required_ids = [self._resolve_skill(ref).id for ref in data.required_skills]
        preferred_ids = [self._resolve_skill(ref).id for ref in data.preferred_skills]
        self.career_roles.set_skills(role, required_skill_ids=required_ids, preferred_skill_ids=preferred_ids)

    # --- learning resources --------------------------------------------------

    def list_learning_resources(self) -> list[LearningResource]:
        return self.learning_resources.list_all()

    def create_learning_resource(self, data: AdminLearningResourceWriteRequest) -> LearningResource:
        resource = self.learning_resources.create(
            title=data.title, description=data.description, url=data.url, provider=data.provider, resource_type=data.resource_type
        )
        self._apply_skills(self.learning_resources, resource, data.skills)
        return resource

    def update_learning_resource(self, resource_id: uuid.UUID, data: AdminLearningResourceWriteRequest) -> LearningResource:
        resource = self.learning_resources.get_by_id(resource_id)
        if resource is None:
            raise NotFoundError("Learning resource not found.")
        self.learning_resources.update(
            resource, title=data.title, description=data.description, url=data.url, provider=data.provider, resource_type=data.resource_type
        )
        self._apply_skills(self.learning_resources, resource, data.skills)
        return resource

    def delete_learning_resource(self, resource_id: uuid.UUID) -> None:
        resource = self.learning_resources.get_by_id(resource_id)
        if resource is None:
            raise NotFoundError("Learning resource not found.")
        self.learning_resources.delete(resource)

    # --- job postings ------------------------------------------------------

    def list_job_postings(self) -> list[JobPosting]:
        return self.job_postings.list_all()

    def create_job_posting(self, data: AdminJobPostingWriteRequest) -> JobPosting:
        job = self.job_postings.create(
            title=data.title,
            company=data.company,
            location=data.location,
            employment_type=data.employment_type,
            is_remote=data.is_remote,
            description=data.description,
            apply_url=data.apply_url,
        )
        self._apply_skills(self.job_postings, job, data.skills)
        return job

    def update_job_posting(self, job_id: uuid.UUID, data: AdminJobPostingWriteRequest) -> JobPosting:
        job = self.job_postings.get_by_id(job_id)
        if job is None:
            raise NotFoundError("Job posting not found.")
        self.job_postings.update(
            job,
            title=data.title,
            company=data.company,
            location=data.location,
            employment_type=data.employment_type,
            is_remote=data.is_remote,
            description=data.description,
            apply_url=data.apply_url,
        )
        self._apply_skills(self.job_postings, job, data.skills)
        return job

    def delete_job_posting(self, job_id: uuid.UUID) -> None:
        job = self.job_postings.get_by_id(job_id)
        if job is None:
            raise NotFoundError("Job posting not found.")
        self.job_postings.delete(job)

    # --- interview questions ------------------------------------------------

    def list_interview_questions(self) -> list[InterviewQuestion]:
        return self.interview_questions.list_all()

    def create_interview_question(self, data: AdminInterviewQuestionWriteRequest) -> InterviewQuestion:
        question = self.interview_questions.create(
            question_text=data.question_text, category=data.category, difficulty=data.difficulty, model_answer=data.model_answer
        )
        self._apply_skills(self.interview_questions, question, data.skills)
        return question

    def update_interview_question(self, question_id: uuid.UUID, data: AdminInterviewQuestionWriteRequest) -> InterviewQuestion:
        question = self.interview_questions.get_by_id(question_id)
        if question is None:
            raise NotFoundError("Interview question not found.")
        self.interview_questions.update(
            question, question_text=data.question_text, category=data.category, difficulty=data.difficulty, model_answer=data.model_answer
        )
        self._apply_skills(self.interview_questions, question, data.skills)
        return question

    def delete_interview_question(self, question_id: uuid.UUID) -> None:
        question = self.interview_questions.get_by_id(question_id)
        if question is None:
            raise NotFoundError("Interview question not found.")
        self.interview_questions.delete(question)
        try:
            # Unlike the other three catalogues, a question can be RESTRICT-
            # referenced by mock_interview_session_questions/_answers once a
            # student has actually used it in a session — flush here (rather
            # than leaving it to the route's later commit) so that foreseeable
            # conflict comes back as a clean 409, not a raw 500.
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                "This question has already been used in a mock interview session and can't be deleted."
            ) from exc

    # --- internals -----------------------------------------------------

    def _resolve_skill(self, ref: AdminSkillRef) -> Skill:
        return self.skills.get_or_create(name=ref.name, category=ref.category)

    def _apply_skills(self, repository, entity, refs: list[AdminSkillRef]) -> None:
        skill_ids = [self._resolve_skill(ref).id for ref in refs]
        repository.set_skills(entity, skill_ids)
