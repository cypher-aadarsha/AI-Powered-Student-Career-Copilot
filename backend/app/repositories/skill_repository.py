import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.skill import Skill, SkillCategory


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, skill_id: uuid.UUID) -> Skill | None:
        return self.db.get(Skill, skill_id)

    def get_by_name(self, name: str) -> Skill | None:
        return self.db.scalar(select(Skill).where(func.lower(Skill.name) == name.strip().lower()))

    def search(self, query: str | None = None, limit: int = 20) -> list[Skill]:
        stmt = select(Skill).order_by(Skill.name).limit(limit)
        if query:
            stmt = stmt.where(func.lower(Skill.name).contains(query.strip().lower()))
        return list(self.db.scalars(stmt))

    def get_or_create(self, *, name: str, category: SkillCategory) -> Skill:
        """Normalizes by case-insensitive name match — the same skill typed
        as "React" or "react" resolves to one catalogue row, never two."""
        existing = self.get_by_name(name)
        if existing:
            return existing
        skill = Skill(name=name.strip(), category=category)
        self.db.add(skill)
        self.db.flush()
        return skill
