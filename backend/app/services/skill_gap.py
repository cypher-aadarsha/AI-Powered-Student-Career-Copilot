"""Explainable skill-gap scoring: a deterministic weighted formula, not a
model — every point earned or missed maps to one visible matched/missing
skill, same design goal as the resume analyzer's MockAIProvider
(app/ai/provider.py). Required skills count double a preferred skill, and a
matched skill earns partial credit based on the student's proficiency
rather than a flat yes/no, so "knows React at expert level" scores higher
than "listed React as a beginner."
"""
import uuid
from dataclasses import dataclass

from app.models.skill import Skill
from app.models.student_profile import StudentProfile
from app.models.student_skill import ProficiencyLevel

REQUIRED_WEIGHT = 2.0
PREFERRED_WEIGHT = 1.0

PROFICIENCY_MULTIPLIER = {
    ProficiencyLevel.beginner: 0.5,
    ProficiencyLevel.intermediate: 0.75,
    ProficiencyLevel.advanced: 1.0,
    ProficiencyLevel.expert: 1.0,
}


@dataclass
class SkillGapResult:
    score: int
    matched_skills: list[tuple[Skill, ProficiencyLevel]]
    missing_required: list[Skill]
    missing_preferred: list[Skill]
    total_required: int
    total_preferred: int
    summary: str


def student_skill_levels(profile: StudentProfile | None) -> dict[uuid.UUID, ProficiencyLevel]:
    """Shared by CareerService and JobService: both need "what does this
    student know, and at what level" as a plain lookup dict before running
    it through compute_skill_gap against a role's or job's skill list."""
    if profile is None:
        return {}
    return {student_skill.skill_id: student_skill.proficiency_level for student_skill in profile.skills}


def compute_skill_gap(
    student_skills: dict[uuid.UUID, ProficiencyLevel],
    required_skills: list[Skill],
    preferred_skills: list[Skill],
) -> SkillGapResult:
    matched: list[tuple[Skill, ProficiencyLevel]] = []
    missing_required: list[Skill] = []
    missing_preferred: list[Skill] = []
    earned = 0.0
    possible = 0.0

    for skill in required_skills:
        possible += REQUIRED_WEIGHT
        level = student_skills.get(skill.id)
        if level is None:
            missing_required.append(skill)
        else:
            matched.append((skill, level))
            earned += REQUIRED_WEIGHT * PROFICIENCY_MULTIPLIER[level]

    for skill in preferred_skills:
        possible += PREFERRED_WEIGHT
        level = student_skills.get(skill.id)
        if level is None:
            missing_preferred.append(skill)
        else:
            matched.append((skill, level))
            earned += PREFERRED_WEIGHT * PROFICIENCY_MULTIPLIER[level]

    score = round(100 * earned / possible) if possible else 0
    matched_required = len(required_skills) - len(missing_required)
    summary = f"You match {matched_required}/{len(required_skills)} required skills"
    if preferred_skills:
        matched_preferred = len(preferred_skills) - len(missing_preferred)
        summary += f" and {matched_preferred}/{len(preferred_skills)} preferred skills"
    summary += f". Overall fit score: {score}/100."

    return SkillGapResult(
        score=score,
        matched_skills=matched,
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        total_required=len(required_skills),
        total_preferred=len(preferred_skills),
        summary=summary,
    )
