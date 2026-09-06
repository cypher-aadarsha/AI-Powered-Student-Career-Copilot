import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning_resource import LearningResource, LearningResourceSkill


class LearningResourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, skill_id: uuid.UUID | None = None) -> list[LearningResource]:
        stmt = select(LearningResource).order_by(LearningResource.title)
        if skill_id is not None:
            stmt = stmt.join(LearningResourceSkill).where(LearningResourceSkill.skill_id == skill_id)
        return list(self.db.scalars(stmt))

    def get_by_id(self, resource_id: uuid.UUID) -> LearningResource | None:
        return self.db.get(LearningResource, resource_id)

    def list_by_skill_ids(self, skill_ids: list[uuid.UUID]) -> list[LearningResource]:
        if not skill_ids:
            return []
        stmt = (
            select(LearningResource)
            .join(LearningResourceSkill)
            .where(LearningResourceSkill.skill_id.in_(skill_ids))
            .distinct()
            .order_by(LearningResource.title)
        )
        return list(self.db.scalars(stmt))
