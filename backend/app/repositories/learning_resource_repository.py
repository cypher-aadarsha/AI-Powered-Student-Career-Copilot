import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning_resource import LearningResource, LearningResourceSkill, ResourceType


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

    def create(
        self, *, title: str, description: str | None, url: str, provider: str, resource_type: ResourceType
    ) -> LearningResource:
        resource = LearningResource(title=title, description=description, url=url, provider=provider, resource_type=resource_type)
        self.db.add(resource)
        self.db.flush()
        return resource

    def update(
        self,
        resource: LearningResource,
        *,
        title: str,
        description: str | None,
        url: str,
        provider: str,
        resource_type: ResourceType,
    ) -> LearningResource:
        resource.title = title
        resource.description = description
        resource.url = url
        resource.provider = provider
        resource.resource_type = resource_type
        self.db.flush()
        return resource

    def delete(self, resource: LearningResource) -> None:
        self.db.delete(resource)

    def set_skills(self, resource: LearningResource, skill_ids: list[uuid.UUID]) -> None:
        for existing in list(resource.skills):
            self.db.delete(existing)
        self.db.flush()
        for skill_id in dict.fromkeys(skill_ids):
            self.db.add(LearningResourceSkill(learning_resource_id=resource.id, skill_id=skill_id))
        self.db.flush()
