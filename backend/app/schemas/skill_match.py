"""Shared shape for "a skill the student has, at what level" — used by both
the career module (Phase 6) and the job-matching module (Phase 7), since
both run their skill lists through the same `skill_gap.compute_skill_gap`.
"""
from pydantic import BaseModel

from app.models.student_skill import ProficiencyLevel
from app.schemas.profile import SkillPublic


class MatchedSkill(BaseModel):
    skill: SkillPublic
    proficiency_level: ProficiencyLevel
