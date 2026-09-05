"""Profile module business logic. Every mutation here is scoped to a single
student_profile_id resolved from the authenticated user — a route can never
pass an arbitrary profile id, and any sub-resource lookup that doesn't
belong to that profile raises NotFoundError (never ForbiddenError, so a
student can't tell someone else's resource id from a nonexistent one).
"""
import logging
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.student_profile import StudentProfile
from app.repositories.certification_repository import CertificationRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.student_skill_repository import StudentSkillRepository
from app.schemas.profile import (
    CertificationWriteRequest,
    ExperienceWriteRequest,
    ProfileUpdateRequest,
    ProjectWriteRequest,
    SkillCreateRequest,
)

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.profiles = ProfileRepository(db)
        self.skills = SkillRepository(db)
        self.student_skills = StudentSkillRepository(db)
        self.projects = ProjectRepository(db)
        self.experiences = ExperienceRepository(db)
        self.certifications = CertificationRepository(db)

    def get_or_create_profile(self, user_id: uuid.UUID) -> StudentProfile:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            profile = self.profiles.create(user_id=user_id)
            logger.info("profile_created user_id=%s", user_id)
        return profile

    def update_profile(self, user_id: uuid.UUID, data: ProfileUpdateRequest) -> StudentProfile:
        profile = self.get_or_create_profile(user_id)
        for field, value in data.model_dump().items():
            setattr(profile, field, value)
        self.db.flush()
        return profile

    # --- skills ---------------------------------------------------------

    def add_skill(self, user_id: uuid.UUID, data: SkillCreateRequest):
        profile = self.get_or_create_profile(user_id)
        skill = self.skills.get_or_create(name=data.name, category=data.category)
        if self.student_skills.get_by_profile_and_skill(profile.id, skill.id):
            raise ConflictError(f'"{skill.name}" is already on your profile.')
        return self.student_skills.create(
            student_profile_id=profile.id, skill_id=skill.id, proficiency_level=data.proficiency_level
        )

    def remove_skill(self, user_id: uuid.UUID, student_skill_id: uuid.UUID) -> None:
        profile = self.get_or_create_profile(user_id)
        student_skill = self.student_skills.get_by_id(student_skill_id)
        if student_skill is None or student_skill.student_profile_id != profile.id:
            raise NotFoundError("Skill not found on your profile.")
        self.student_skills.delete(student_skill)

    # --- projects ---------------------------------------------------------

    def add_project(self, user_id: uuid.UUID, data: ProjectWriteRequest):
        profile = self.get_or_create_profile(user_id)
        self._ensure_skills_exist(data.skill_ids)
        return self.projects.create(
            student_profile_id=profile.id,
            title=data.title,
            description=data.description,
            repo_url=data.repo_url,
            demo_url=data.demo_url,
            start_date=data.start_date,
            end_date=data.end_date,
            skill_ids=data.skill_ids,
        )

    def update_project(self, user_id: uuid.UUID, project_id: uuid.UUID, data: ProjectWriteRequest):
        profile = self.get_or_create_profile(user_id)
        project = self.projects.get_by_id(project_id)
        if project is None or project.student_profile_id != profile.id:
            raise NotFoundError("Project not found on your profile.")
        self._ensure_skills_exist(data.skill_ids)
        return self.projects.update(
            project,
            title=data.title,
            description=data.description,
            repo_url=data.repo_url,
            demo_url=data.demo_url,
            start_date=data.start_date,
            end_date=data.end_date,
            skill_ids=data.skill_ids,
        )

    def delete_project(self, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
        profile = self.get_or_create_profile(user_id)
        project = self.projects.get_by_id(project_id)
        if project is None or project.student_profile_id != profile.id:
            raise NotFoundError("Project not found on your profile.")
        self.projects.delete(project)

    # --- experiences ------------------------------------------------------

    def add_experience(self, user_id: uuid.UUID, data: ExperienceWriteRequest):
        profile = self.get_or_create_profile(user_id)
        return self.experiences.create(student_profile_id=profile.id, **data.model_dump())

    def update_experience(self, user_id: uuid.UUID, experience_id: uuid.UUID, data: ExperienceWriteRequest):
        profile = self.get_or_create_profile(user_id)
        experience = self.experiences.get_by_id(experience_id)
        if experience is None or experience.student_profile_id != profile.id:
            raise NotFoundError("Experience not found on your profile.")
        return self.experiences.update(experience, **data.model_dump())

    def delete_experience(self, user_id: uuid.UUID, experience_id: uuid.UUID) -> None:
        profile = self.get_or_create_profile(user_id)
        experience = self.experiences.get_by_id(experience_id)
        if experience is None or experience.student_profile_id != profile.id:
            raise NotFoundError("Experience not found on your profile.")
        self.experiences.delete(experience)

    # --- certifications -----------------------------------------------------

    def add_certification(self, user_id: uuid.UUID, data: CertificationWriteRequest):
        profile = self.get_or_create_profile(user_id)
        return self.certifications.create(student_profile_id=profile.id, **data.model_dump())

    def update_certification(self, user_id: uuid.UUID, certification_id: uuid.UUID, data: CertificationWriteRequest):
        profile = self.get_or_create_profile(user_id)
        certification = self.certifications.get_by_id(certification_id)
        if certification is None or certification.student_profile_id != profile.id:
            raise NotFoundError("Certification not found on your profile.")
        return self.certifications.update(certification, **data.model_dump())

    def delete_certification(self, user_id: uuid.UUID, certification_id: uuid.UUID) -> None:
        profile = self.get_or_create_profile(user_id)
        certification = self.certifications.get_by_id(certification_id)
        if certification is None or certification.student_profile_id != profile.id:
            raise NotFoundError("Certification not found on your profile.")
        self.certifications.delete(certification)

    # --- helpers -----------------------------------------------------------

    def _ensure_skills_exist(self, skill_ids: list[uuid.UUID]) -> None:
        for skill_id in skill_ids:
            if self.skills.get_by_id(skill_id) is None:
                raise NotFoundError(f"Skill {skill_id} does not exist.")
