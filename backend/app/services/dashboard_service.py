"""Career dashboard (Phase 9): a single read-only aggregate view composed
from the services every earlier phase already built — profile, resumes,
career/job matching, and mock interviews. Nothing new is computed here
except profile completion and the "suggested actions" rules; everything
else is exactly what its own module already returns, just gathered into
one response so the frontend isn't making six round trips to render one
page.
"""
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.career_role import CareerRole
from app.models.job_posting import JobPosting
from app.models.mock_interview import MockInterviewSession, SessionStatus
from app.models.resume import Resume
from app.models.student_profile import StudentProfile
from app.repositories.mock_interview_repository import MockInterviewSessionRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.career_service import CareerService
from app.services.job_service import JobService
from app.services.skill_gap import SkillGapResult

TOP_MATCHES_LIMIT = 3
MAX_SUGGESTIONS = 4

CHECKLIST_RULES: list[tuple[str, Callable[[StudentProfile], bool]]] = [
    ("Academic info (university, degree, semester)", lambda p: bool(p.university and p.degree and p.semester)),
    ("A short bio", lambda p: bool(p.bio)),
    ("At least one skill", lambda p: len(p.skills) >= 1),
    ("At least three skills", lambda p: len(p.skills) >= 3),
    ("At least one project", lambda p: len(p.projects) >= 1),
    ("Work or internship experience", lambda p: len(p.experiences) >= 1),
    ("A certification", lambda p: len(p.certifications) >= 1),
    ("A resume uploaded", lambda p: len(p.resumes) >= 1),
    ("GitHub, LinkedIn, or portfolio link", lambda p: bool(p.github_url or p.linkedin_url or p.portfolio_url)),
]


@dataclass
class ChecklistItem:
    label: str
    done: bool


@dataclass
class ProfileCompletion:
    score: int
    checklist: list[ChecklistItem]


@dataclass
class InterviewStats:
    total_sessions: int
    completed_sessions: int
    average_score: int | None


@dataclass
class DashboardData:
    profile_completion: ProfileCompletion
    latest_resume: Resume | None
    top_career_matches: list[tuple[CareerRole, SkillGapResult]]
    top_job_matches: list[tuple[JobPosting, SkillGapResult]]
    skill_count: int
    interview_stats: InterviewStats
    suggested_actions: list[str]


def compute_profile_completion(profile: StudentProfile) -> ProfileCompletion:
    checklist = [ChecklistItem(label=label, done=rule(profile)) for label, rule in CHECKLIST_RULES]
    score = round(100 * sum(1 for item in checklist if item.done) / len(checklist))
    return ProfileCompletion(score=score, checklist=checklist)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.profiles = ProfileRepository(db)
        self.careers = CareerService(db)
        self.jobs = JobService(db)
        self.interview_sessions = MockInterviewSessionRepository(db)

    def get_dashboard(self, user_id: uuid.UUID) -> DashboardData:
        profile = self._get_or_create_profile(user_id)
        completion = compute_profile_completion(profile)
        latest_resume = profile.resumes[0] if profile.resumes else None

        top_careers = self.careers.list_roles_ranked(user_id)[:TOP_MATCHES_LIMIT]
        top_jobs = self.jobs.list_jobs_ranked(user_id)[:TOP_MATCHES_LIMIT]

        sessions = self.interview_sessions.list_by_profile(profile.id)
        interview_stats = self._compute_interview_stats(sessions)

        suggestions = self._suggest_actions(profile, latest_resume, top_careers, interview_stats)

        return DashboardData(
            profile_completion=completion,
            latest_resume=latest_resume,
            top_career_matches=top_careers,
            top_job_matches=top_jobs,
            skill_count=len(profile.skills),
            interview_stats=interview_stats,
            suggested_actions=suggestions,
        )

    # --- internals -----------------------------------------------------

    def _get_or_create_profile(self, user_id: uuid.UUID) -> StudentProfile:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            profile = self.profiles.create(user_id=user_id)
        return profile

    def _compute_interview_stats(self, sessions: list[MockInterviewSession]) -> InterviewStats:
        completed = [s for s in sessions if s.status == SessionStatus.completed]
        all_scores = [
            answer.ai_score for session in sessions for answer in session.answers if answer.ai_score is not None
        ]
        average = round(sum(all_scores) / len(all_scores)) if all_scores else None
        return InterviewStats(total_sessions=len(sessions), completed_sessions=len(completed), average_score=average)

    def _suggest_actions(
        self,
        profile: StudentProfile,
        latest_resume: Resume | None,
        top_careers: list[tuple[CareerRole, SkillGapResult]],
        interview_stats: InterviewStats,
    ) -> list[str]:
        suggestions: list[str] = []

        if latest_resume is None:
            suggestions.append("Upload your resume to get instant AI feedback and detected skills.")
        if len(profile.skills) < 3:
            suggestions.append("Add at least 3 skills to your profile for more accurate career matches.")
        if len(profile.projects) == 0:
            suggestions.append("Add a project to show recruiters what you've actually built.")
        if interview_stats.total_sessions == 0:
            suggestions.append("Start a mock interview to practice answering real questions.")
        if top_careers and top_careers[0][1].score < 50:
            role_title = top_careers[0][0].title
            suggestions.append(
                f"Your best career match ({role_title}) is only {top_careers[0][1].score}% — check its "
                "missing skills and learning plan."
            )

        return suggestions[:MAX_SUGGESTIONS]
