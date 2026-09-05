import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student_skill import ProficiencyLevel, SkillSource, StudentSkill


class StudentSkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_profile(self, student_profile_id: uuid.UUID) -> list[StudentSkill]:
        stmt = select(StudentSkill).where(StudentSkill.student_profile_id == student_profile_id)
        return list(self.db.scalars(stmt))

    def get_by_id(self, student_skill_id: uuid.UUID) -> StudentSkill | None:
        return self.db.get(StudentSkill, student_skill_id)

    def get_by_profile_and_skill(self, student_profile_id: uuid.UUID, skill_id: uuid.UUID) -> StudentSkill | None:
        stmt = select(StudentSkill).where(
            StudentSkill.student_profile_id == student_profile_id, StudentSkill.skill_id == skill_id
        )
        return self.db.scalar(stmt)

    def create(
        self,
        *,
        student_profile_id: uuid.UUID,
        skill_id: uuid.UUID,
        proficiency_level: ProficiencyLevel,
        source: SkillSource = SkillSource.manual,
    ) -> StudentSkill:
        student_skill = StudentSkill(
            student_profile_id=student_profile_id,
            skill_id=skill_id,
            proficiency_level=proficiency_level,
            source=source,
        )
        self.db.add(student_skill)
        self.db.flush()
        return student_skill

    def delete(self, student_skill: StudentSkill) -> None:
        self.db.delete(student_skill)
