"""Seeds a curated set of learning resources tagged against the shared skill
catalogue (mostly skills already seeded by seed/career_roles.py). Every URL
here points at a real, stable, top-level page from a well-known
documentation/course provider — not a fabricated or dead link.

Coverage is deliberately partial, not exhaustive: every required skill on
the more common roles (Backend/Frontend/Full-Stack Developer, Data
Scientist, DevOps Engineer) has at least one resource; a few niche skills
(e.g. Cryptography, Test Case Design) don't yet — a known gap, not a bug,
easy to close by appending to RESOURCES below.

Idempotent: re-running skips any resource whose title already exists.

Usage (from backend/, with DATABASE_URL pointed at the target database):
    python -m seed.learning_resources
"""
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.learning_resource import LearningResource, LearningResourceSkill, ResourceType
from app.models.skill import SkillCategory
from app.repositories.learning_resource_repository import LearningResourceRepository
from app.repositories.skill_repository import SkillRepository

# (title, url, provider, resource_type, [(skill name, category), ...])
RESOURCES = [
    (
        "The Python Tutorial",
        "https://docs.python.org/3/tutorial/index.html",
        "Python Software Foundation",
        ResourceType.documentation,
        [("Python", SkillCategory.programming_language)],
    ),
    (
        "Real Python",
        "https://realpython.com/",
        "Real Python",
        ResourceType.tutorial,
        [("Python", SkillCategory.programming_language)],
    ),
    (
        "JavaScript Guide",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "MDN Web Docs",
        ResourceType.documentation,
        [("JavaScript", SkillCategory.programming_language)],
    ),
    (
        "HTML Developer Guide",
        "https://developer.mozilla.org/en-US/docs/Web/HTML",
        "MDN Web Docs",
        ResourceType.documentation,
        [("HTML", SkillCategory.technical)],
    ),
    (
        "CSS Developer Guide",
        "https://developer.mozilla.org/en-US/docs/Web/CSS",
        "MDN Web Docs",
        ResourceType.documentation,
        [("CSS", SkillCategory.technical)],
    ),
    (
        "Learn React",
        "https://react.dev/learn",
        "react.dev",
        ResourceType.documentation,
        [("React", SkillCategory.framework)],
    ),
    (
        "SQLBolt — Interactive SQL Lessons",
        "https://sqlbolt.com/",
        "SQLBolt",
        ResourceType.tutorial,
        [("SQL", SkillCategory.technical)],
    ),
    (
        "Git Documentation",
        "https://git-scm.com/doc",
        "Git",
        ResourceType.documentation,
        [("Git", SkillCategory.tool)],
    ),
    (
        "Docker Get Started Guide",
        "https://docs.docker.com/get-started/",
        "Docker",
        ResourceType.documentation,
        [("Docker", SkillCategory.tool)],
    ),
    (
        "PostgreSQL Tutorial",
        "https://www.postgresql.org/docs/current/tutorial.html",
        "PostgreSQL Global Development Group",
        ResourceType.documentation,
        [("PostgreSQL", SkillCategory.technical)],
    ),
    (
        "FastAPI Tutorial",
        "https://fastapi.tiangolo.com/tutorial/",
        "FastAPI",
        ResourceType.documentation,
        [("FastAPI", SkillCategory.framework), ("REST APIs", SkillCategory.technical)],
    ),
    (
        "TypeScript Handbook",
        "https://www.typescriptlang.org/docs/handbook/intro.html",
        "TypeScript",
        ResourceType.documentation,
        [("TypeScript", SkillCategory.programming_language)],
    ),
    (
        "Next.js Learn Course",
        "https://nextjs.org/learn",
        "Vercel",
        ResourceType.course,
        [("Next.js", SkillCategory.framework)],
    ),
    (
        "Statistics and Probability",
        "https://www.khanacademy.org/math/statistics-probability",
        "Khan Academy",
        ResourceType.course,
        [("Statistics", SkillCategory.technical)],
    ),
    (
        "Machine Learning Crash Course",
        "https://developers.google.com/machine-learning/crash-course",
        "Google",
        ResourceType.course,
        [("Machine Learning", SkillCategory.technical)],
    ),
    (
        "pandas — Getting Started",
        "https://pandas.pydata.org/docs/getting_started/index.html",
        "pandas",
        ResourceType.documentation,
        [("Pandas", SkillCategory.tool)],
    ),
    (
        "The Linux Command Line",
        "https://linuxcommand.org/tlcl.php",
        "linuxcommand.org",
        ResourceType.book,
        [("Linux", SkillCategory.technical)],
    ),
    (
        "Kubernetes Documentation",
        "https://kubernetes.io/docs/home/",
        "Kubernetes",
        ResourceType.documentation,
        [("Kubernetes", SkillCategory.tool)],
    ),
    (
        "AWS Skill Builder",
        "https://skillbuilder.aws/",
        "Amazon Web Services",
        ResourceType.course,
        [("AWS", SkillCategory.tool)],
    ),
    (
        "OWASP Top Ten",
        "https://owasp.org/www-project-top-ten/",
        "OWASP",
        ResourceType.documentation,
        [("Security Fundamentals", SkillCategory.technical)],
    ),
    (
        "Android Developer Courses",
        "https://developer.android.com/courses",
        "Google",
        ResourceType.course,
        [("Android SDK", SkillCategory.framework)],
    ),
    (
        "Selenium Documentation",
        "https://www.selenium.dev/documentation/",
        "Selenium",
        ResourceType.documentation,
        [("Selenium", SkillCategory.tool)],
    ),
]


def seed_learning_resources(db: Session) -> int:
    """Inserts every resource in RESOURCES that doesn't already exist (by
    title). Returns how many were created. Flushes but does not commit."""
    resources = LearningResourceRepository(db)
    skills = SkillRepository(db)
    existing_titles = {resource.title for resource in resources.list_all()}

    created = 0
    for title, url, provider, resource_type, skill_specs in RESOURCES:
        if title in existing_titles:
            continue
        resource = LearningResource(title=title, url=url, provider=provider, resource_type=resource_type)
        db.add(resource)
        db.flush()
        for name, category in skill_specs:
            skill = skills.get_or_create(name=name, category=category)
            db.add(LearningResourceSkill(learning_resource_id=resource.id, skill_id=skill.id))
        created += 1

    db.flush()
    return created


def run() -> None:
    db = SessionLocal()
    try:
        created = seed_learning_resources(db)
        db.commit()
        print(f"Seeded {created} new learning resource(s); {len(RESOURCES) - created} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
