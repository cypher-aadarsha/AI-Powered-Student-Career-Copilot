"""Career role browsing + skill-gap matching (Phase 6). Unlike the profile
sub-resources, a CareerRole is shared platform data, not owned by a student
— there's no ownership check on the role itself, only a plain 404 when the
id doesn't exist. What IS scoped to the student is the score: it's computed
fresh from their current StudentSkill rows on every request.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.career_role import CareerRole, RoleSkillImportance
from app.models.student_skill import ProficiencyLevel
from app.repositories.career_role_repository import CareerRoleRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.skill_gap import SkillGapResult, compute_skill_gap, student_skill_levels


class CareerService:
    def __init__(self, db: Session):
        self.db = db
        self.profiles = ProfileRepository(db)
        self.career_roles = CareerRoleRepository(db)

    def list_roles_ranked(self, user_id: uuid.UUID) -> list[tuple[CareerRole, SkillGapResult]]:
        student_skills = self._student_skills(user_id)
        results = [
            (role, self._gap_for_role(role, student_skills)) for role in self.career_roles.list_all()
        ]
        results.sort(key=lambda pair: pair[1].score, reverse=True)
        return results

    def get_role_detail(self, user_id: uuid.UUID, role_id: uuid.UUID) -> tuple[CareerRole, SkillGapResult]:
        role = self.career_roles.get_by_id(role_id)
        if role is None:
            raise NotFoundError("Career role not found.")
        student_skills = self._student_skills(user_id)
        return role, self._gap_for_role(role, student_skills)

    # --- internals -----------------------------------------------------

    def _student_skills(self, user_id: uuid.UUID) -> dict[uuid.UUID, ProficiencyLevel]:
        return student_skill_levels(self.profiles.get_by_user_id(user_id))

    def _gap_for_role(self, role: CareerRole, student_skills: dict[uuid.UUID, ProficiencyLevel]) -> SkillGapResult:
        required = [rs.skill for rs in role.skills if rs.importance == RoleSkillImportance.required]
        preferred = [rs.skill for rs in role.skills if rs.importance == RoleSkillImportance.preferred]
        return compute_skill_gap(student_skills, required, preferred)
