"""Seeds demo job postings for Phase 7's skill-matching feature.

Every company here is fictional and every `apply_url` points at
example.com (RFC 2606's reserved documentation domain) — this is sample
data to demonstrate the matching feature, not a live job board, and it
must never be mistaken for real postings or real employers.

Idempotent: re-running skips any posting whose title+company already exists.

Usage (from backend/, with DATABASE_URL pointed at the target database):
    python -m seed.job_postings
"""
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.job_posting import JobEmploymentType, JobPosting, JobPostingSkill
from app.models.skill import SkillCategory
from app.repositories.job_posting_repository import JobPostingRepository
from app.repositories.skill_repository import SkillRepository

# (title, company, location, employment_type, is_remote, description, apply_slug, [(skill, category), ...])
JOBS = [
    (
        "Backend Developer Intern",
        "Nimbus Cloud Labs",
        "Kathmandu, Nepal",
        JobEmploymentType.internship,
        False,
        "Support the API team building and testing internal services.",
        "nimbus-backend-intern",
        [("Python", SkillCategory.programming_language), ("SQL", SkillCategory.technical), ("Git", SkillCategory.tool)],
    ),
    (
        "Junior Frontend Developer",
        "PixelForge Studios",
        "Pokhara, Nepal",
        JobEmploymentType.full_time,
        True,
        "Build responsive UI components for client web products.",
        "pixelforge-frontend-junior",
        [
            ("JavaScript", SkillCategory.programming_language),
            ("HTML", SkillCategory.technical),
            ("CSS", SkillCategory.technical),
            ("React", SkillCategory.framework),
        ],
    ),
    (
        "Full-Stack Engineer",
        "BrightPath Software",
        "Lalitpur, Nepal",
        JobEmploymentType.full_time,
        False,
        "Own features end-to-end across a React frontend and a Python API.",
        "brightpath-fullstack-engineer",
        [
            ("JavaScript", SkillCategory.programming_language),
            ("Python", SkillCategory.programming_language),
            ("SQL", SkillCategory.technical),
            ("Git", SkillCategory.tool),
            ("React", SkillCategory.framework),
        ],
    ),
    (
        "Data Analyst Intern",
        "Northstar Analytics",
        "Kathmandu, Nepal",
        JobEmploymentType.internship,
        True,
        "Turn raw datasets into dashboards and reports for internal teams.",
        "northstar-data-analyst-intern",
        [
            ("SQL", SkillCategory.technical),
            ("Statistics", SkillCategory.technical),
            ("Python", SkillCategory.programming_language),
        ],
    ),
    (
        "DevOps Engineer",
        "Everest DevOps Co.",
        "Kathmandu, Nepal",
        JobEmploymentType.full_time,
        True,
        "Maintain CI/CD pipelines and container infrastructure.",
        "everest-devops-engineer",
        [("Linux", SkillCategory.technical), ("Docker", SkillCategory.tool), ("Git", SkillCategory.tool), ("AWS", SkillCategory.tool)],
    ),
    (
        "Machine Learning Intern",
        "Himalayan Data Works",
        "Kathmandu, Nepal",
        JobEmploymentType.internship,
        False,
        "Assist in training and evaluating predictive models.",
        "himalayan-ml-intern",
        [
            ("Python", SkillCategory.programming_language),
            ("Statistics", SkillCategory.technical),
            ("Machine Learning", SkillCategory.technical),
        ],
    ),
    (
        "QA Engineer",
        "TestCraft QA Services",
        "Biratnagar, Nepal",
        JobEmploymentType.contract,
        False,
        "Write and run test plans across web and API surfaces.",
        "testcraft-qa-engineer",
        [
            ("Manual Testing", SkillCategory.technical),
            ("SQL", SkillCategory.technical),
            ("Selenium", SkillCategory.tool),
        ],
    ),
    (
        "Security Analyst",
        "SecureGrid Systems",
        "Kathmandu, Nepal",
        JobEmploymentType.full_time,
        True,
        "Monitor systems and investigate potential security incidents.",
        "securegrid-security-analyst",
        [
            ("Networking", SkillCategory.technical),
            ("Linux", SkillCategory.technical),
            ("Security Fundamentals", SkillCategory.technical),
        ],
    ),
    (
        "Mobile App Developer",
        "Lumina Mobile",
        "Pokhara, Nepal",
        JobEmploymentType.full_time,
        False,
        "Build and maintain Android features for a consumer app.",
        "lumina-mobile-developer",
        [
            ("Java", SkillCategory.programming_language),
            ("Kotlin", SkillCategory.programming_language),
            ("Git", SkillCategory.tool),
        ],
    ),
    (
        "Backend Developer (Part-Time)",
        "GreenByte Solutions",
        "Kathmandu, Nepal",
        JobEmploymentType.part_time,
        True,
        "Extend REST APIs for a small product team.",
        "greenbyte-backend-parttime",
        [
            ("Python", SkillCategory.programming_language),
            ("REST APIs", SkillCategory.technical),
            ("PostgreSQL", SkillCategory.technical),
        ],
    ),
]


def seed_job_postings(db: Session) -> int:
    """Inserts every posting in JOBS that doesn't already exist (matched by
    title+company). Returns how many were created. Flushes but does not
    commit."""
    jobs = JobPostingRepository(db)
    skills = SkillRepository(db)
    existing = {(job.title, job.company) for job in jobs.list_all()}

    created = 0
    for title, company, location, employment_type, is_remote, description, slug, skill_specs in JOBS:
        if (title, company) in existing:
            continue
        job = JobPosting(
            title=title,
            company=company,
            location=location,
            employment_type=employment_type,
            is_remote=is_remote,
            description=description,
            apply_url=f"https://example.com/careers/{slug}",
        )
        db.add(job)
        db.flush()
        for name, category in skill_specs:
            skill = skills.get_or_create(name=name, category=category)
            db.add(JobPostingSkill(job_posting_id=job.id, skill_id=skill.id))
        created += 1

    db.flush()
    return created


def run() -> None:
    db = SessionLocal()
    try:
        created = seed_job_postings(db)
        db.commit()
        print(f"Seeded {created} new job posting(s); {len(JOBS) - created} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
