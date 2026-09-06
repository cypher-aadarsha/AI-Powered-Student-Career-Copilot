"""Learning-resource browsing plus skill-gap-driven recommendations
(Phase 7). The recommendation flow reuses CareerService's skill-gap output
rather than recomputing it — "what's missing" is Phase 6's job, "how do I
learn it" is this module's.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.career_role import CareerRole
from app.models.learning_resource import LearningResource
from app.models.skill import Skill
from app.repositories.learning_resource_repository import LearningResourceRepository
from app.services.career_service import CareerService


class LearningService:
    def __init__(self, db: Session):
        self.db = db
        self.resources = LearningResourceRepository(db)
        self.careers = CareerService(db)

    def list_resources(self, skill_id: uuid.UUID | None = None) -> list[LearningResource]:
        return self.resources.list_all(skill_id)

    def get_resource(self, resource_id: uuid.UUID) -> LearningResource:
        resource = self.resources.get_by_id(resource_id)
        if resource is None:
            raise NotFoundError("Learning resource not found.")
        return resource

    def get_role_learning_plan(
        self, user_id: uuid.UUID, role_id: uuid.UUID
    ) -> tuple[CareerRole, list[tuple[Skill, list[LearningResource]]], list[tuple[Skill, list[LearningResource]]]]:
        role, gap = self.careers.get_role_detail(user_id, role_id)
        missing_required = self._skills_with_resources(gap.missing_required)
        missing_preferred = self._skills_with_resources(gap.missing_preferred)
        return role, missing_required, missing_preferred

    def _skills_with_resources(self, skills: list[Skill]) -> list[tuple[Skill, list[LearningResource]]]:
        return [(skill, self.resources.list_all(skill_id=skill.id)) for skill in skills]
