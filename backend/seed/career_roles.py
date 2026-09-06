"""Seeds the shared career-role catalogue that Phase 6's skill-gap matching
compares a student's profile against. Roles are platform-curated, not
student-authored (see app/models/career_role.py), so this script — not an
API endpoint — is how they get into the database.

Idempotent: re-running skips any role whose title already exists, so it's
safe to run again after adding new entries to ROLES below.

Usage (from backend/, with DATABASE_URL pointed at the target database):
    python -m seed.career_roles
"""
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.career_role import CareerRole, CareerRoleSkill, RoleSkillImportance
from app.models.skill import SkillCategory
from app.repositories.career_role_repository import CareerRoleRepository
from app.repositories.skill_repository import SkillRepository

# (skill name, category) pairs — resolved through SkillRepository.get_or_create,
# so a skill already in the catalogue (e.g. added by a student) is reused
# rather than duplicated.
ROLES = [
    {
        "title": "Backend Developer",
        "description": "Designs and builds server-side APIs, databases, and business logic.",
        "required": [
            ("Python", SkillCategory.programming_language),
            ("SQL", SkillCategory.technical),
            ("REST APIs", SkillCategory.technical),
            ("Git", SkillCategory.tool),
        ],
        "preferred": [
            ("Docker", SkillCategory.tool),
            ("PostgreSQL", SkillCategory.technical),
            ("FastAPI", SkillCategory.framework),
        ],
    },
    {
        "title": "Frontend Developer",
        "description": "Builds user-facing web interfaces with a focus on usability and performance.",
        "required": [
            ("JavaScript", SkillCategory.programming_language),
            ("HTML", SkillCategory.technical),
            ("CSS", SkillCategory.technical),
            ("React", SkillCategory.framework),
        ],
        "preferred": [
            ("TypeScript", SkillCategory.programming_language),
            ("Next.js", SkillCategory.framework),
            ("Git", SkillCategory.tool),
        ],
    },
    {
        "title": "Full-Stack Developer",
        "description": "Works across both the frontend and backend of a web application.",
        "required": [
            ("JavaScript", SkillCategory.programming_language),
            ("Python", SkillCategory.programming_language),
            ("SQL", SkillCategory.technical),
            ("Git", SkillCategory.tool),
        ],
        "preferred": [
            ("React", SkillCategory.framework),
            ("Docker", SkillCategory.tool),
            ("REST APIs", SkillCategory.technical),
        ],
    },
    {
        "title": "Data Scientist",
        "description": "Analyzes data and builds models to extract insights and predictions.",
        "required": [
            ("Python", SkillCategory.programming_language),
            ("SQL", SkillCategory.technical),
            ("Statistics", SkillCategory.technical),
            ("Machine Learning", SkillCategory.technical),
        ],
        "preferred": [
            ("Pandas", SkillCategory.tool),
            ("Data Visualization", SkillCategory.technical),
            ("R", SkillCategory.programming_language),
        ],
    },
    {
        "title": "DevOps Engineer",
        "description": "Automates and manages build, deployment, and infrastructure pipelines.",
        "required": [
            ("Linux", SkillCategory.technical),
            ("Docker", SkillCategory.tool),
            ("Git", SkillCategory.tool),
            ("CI/CD", SkillCategory.technical),
        ],
        "preferred": [
            ("Kubernetes", SkillCategory.tool),
            ("AWS", SkillCategory.tool),
            ("Bash Scripting", SkillCategory.technical),
        ],
    },
    {
        "title": "Mobile App Developer",
        "description": "Builds native or cross-platform mobile applications.",
        "required": [
            ("Java", SkillCategory.programming_language),
            ("Kotlin", SkillCategory.programming_language),
            ("Android SDK", SkillCategory.framework),
            ("Git", SkillCategory.tool),
        ],
        "preferred": [
            ("Flutter", SkillCategory.framework),
            ("REST APIs", SkillCategory.technical),
            ("Firebase", SkillCategory.tool),
        ],
    },
    {
        "title": "QA / Test Engineer",
        "description": "Designs and executes tests to verify software quality before release.",
        "required": [
            ("Manual Testing", SkillCategory.technical),
            ("Test Case Design", SkillCategory.technical),
            ("Git", SkillCategory.tool),
            ("SQL", SkillCategory.technical),
        ],
        "preferred": [
            ("Selenium", SkillCategory.tool),
            ("Automation Testing", SkillCategory.technical),
            ("API Testing", SkillCategory.technical),
        ],
    },
    {
        "title": "Cybersecurity Analyst",
        "description": "Protects systems and data by identifying and mitigating security risks.",
        "required": [
            ("Networking", SkillCategory.technical),
            ("Linux", SkillCategory.technical),
            ("Security Fundamentals", SkillCategory.technical),
            ("Cryptography", SkillCategory.technical),
        ],
        "preferred": [
            ("Penetration Testing", SkillCategory.technical),
            ("SIEM Tools", SkillCategory.tool),
            ("Python", SkillCategory.programming_language),
        ],
    },
]


def seed_career_roles(db: Session) -> int:
    """Inserts every role in ROLES that doesn't already exist (by title).
    Returns how many new roles were created. Flushes but does not commit —
    the caller decides the transaction boundary (the CLI entrypoint below
    commits; a test can share the transaction with its own fixtures).
    """
    career_roles = CareerRoleRepository(db)
    skills = SkillRepository(db)
    existing_titles = {role.title for role in career_roles.list_all()}

    created = 0
    for role_data in ROLES:
        if role_data["title"] in existing_titles:
            continue
        role = CareerRole(title=role_data["title"], description=role_data["description"])
        db.add(role)
        db.flush()
        for name, category in role_data["required"]:
            skill = skills.get_or_create(name=name, category=category)
            db.add(CareerRoleSkill(career_role_id=role.id, skill_id=skill.id, importance=RoleSkillImportance.required))
        for name, category in role_data["preferred"]:
            skill = skills.get_or_create(name=name, category=category)
            db.add(CareerRoleSkill(career_role_id=role.id, skill_id=skill.id, importance=RoleSkillImportance.preferred))
        created += 1

    db.flush()
    return created


def run() -> None:
    db = SessionLocal()
    try:
        created = seed_career_roles(db)
        db.commit()
        print(f"Seeded {created} new career role(s); {len(ROLES) - created} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
