import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.career_role import CareerRole, CareerRoleSkill, RoleSkillImportance


class CareerRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[CareerRole]:
        stmt = select(CareerRole).order_by(CareerRole.title)
        return list(self.db.scalars(stmt))

    def get_by_id(self, role_id: uuid.UUID) -> CareerRole | None:
        return self.db.get(CareerRole, role_id)

    def get_by_title(self, title: str) -> CareerRole | None:
        return self.db.scalar(select(CareerRole).where(CareerRole.title == title))

    def create(self, *, title: str, description: str | None) -> CareerRole:
        role = CareerRole(title=title, description=description)
        self.db.add(role)
        self.db.flush()
        return role

    def update(self, role: CareerRole, *, title: str, description: str | None) -> CareerRole:
        role.title = title
        role.description = description
        self.db.flush()
        return role

    def delete(self, role: CareerRole) -> None:
        self.db.delete(role)

    def set_skills(
        self, role: CareerRole, *, required_skill_ids: list[uuid.UUID], preferred_skill_ids: list[uuid.UUID]
    ) -> None:
        for existing in list(role.skills):
            self.db.delete(existing)
        self.db.flush()
        seen: set[uuid.UUID] = set()
        for skill_id in required_skill_ids:
            if skill_id in seen:
                continue
            seen.add(skill_id)
            self.db.add(CareerRoleSkill(career_role_id=role.id, skill_id=skill_id, importance=RoleSkillImportance.required))
        for skill_id in preferred_skill_ids:
            if skill_id in seen:
                continue  # a skill can't be both required and preferred (unique constraint per role+skill)
            seen.add(skill_id)
            self.db.add(CareerRoleSkill(career_role_id=role.id, skill_id=skill_id, importance=RoleSkillImportance.preferred))
        self.db.flush()
