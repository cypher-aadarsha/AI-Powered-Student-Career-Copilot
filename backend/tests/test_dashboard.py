"""Coverage for Phase 9: the dashboard aggregation endpoint — profile
completion scoring, latest-resume summary, top career/job matches, mock
interview stats, and the rule-based suggested-actions list.
"""
import uuid

import pytest

from app.models.resume import Resume, ResumeStatus
from app.repositories.profile_repository import ProfileRepository
from app.services.dashboard_service import compute_profile_completion
from seed.career_roles import seed_career_roles
from seed.interview_questions import seed_interview_questions
from seed.job_postings import seed_job_postings

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}


@pytest.fixture(autouse=True)
def _seed_catalogue(db_session):
    seed_career_roles(db_session)
    seed_job_postings(db_session)
    seed_interview_questions(db_session)


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_skill(client, headers, name: str, proficiency: str = "intermediate") -> None:
    response = client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": name, "category": "technical", "proficiency_level": proficiency},
    )
    assert response.status_code == 201


def test_get_dashboard_without_auth_returns_401(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_dashboard_for_a_brand_new_profile(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]

    assert body["profile_completion"]["score"] == 0
    assert all(not item["done"] for item in body["profile_completion"]["checklist"])
    assert body["latest_resume"] is None
    assert body["skill_count"] == 0
    assert body["interview_stats"] == {"total_sessions": 0, "completed_sessions": 0, "average_score": None}
    # every seeded role/job scores 0 with no skills, but they're still listed
    assert len(body["top_career_matches"]) <= 3
    assert all(item["score"] == 0 for item in body["top_career_matches"])
    assert len(body["top_job_matches"]) <= 3

    suggestions = " ".join(body["suggested_actions"]).lower()
    assert "resume" in suggestions
    assert "skill" in suggestions
    assert "project" in suggestions
    assert "mock interview" in suggestions


def test_dashboard_reflects_skills_and_drops_the_skills_suggestion(client):
    headers = _auth_headers(client)
    for skill in ("Python", "SQL", "Git"):
        _add_skill(client, headers, skill)

    response = client.get("/api/v1/dashboard", headers=headers)
    body = response.json()["data"]
    assert body["skill_count"] == 3
    assert body["profile_completion"]["score"] > 0
    suggestions = " ".join(body["suggested_actions"]).lower()
    assert "add at least 3 skills" not in suggestions


def test_dashboard_shows_the_latest_resume(client, db_session):
    headers = _auth_headers(client)
    user_id = uuid.UUID(client.get("/api/v1/users/me", headers=headers).json()["data"]["id"])
    profile = ProfileRepository(db_session).get_by_user_id(user_id)
    if profile is None:
        profile = ProfileRepository(db_session).create(user_id=user_id)
    db_session.add(
        Resume(
            student_profile_id=profile.id,
            original_filename="resume.pdf",
            storage_path="storage/resumes/x/resume.pdf",
            mime_type="application/pdf",
            file_size_bytes=1234,
            status=ResumeStatus.parsed,
            ai_score=72,
        )
    )
    db_session.flush()

    response = client.get("/api/v1/dashboard", headers=headers)
    body = response.json()["data"]
    assert body["latest_resume"]["original_filename"] == "resume.pdf"
    assert body["latest_resume"]["ai_score"] == 72
    assert body["latest_resume"]["status"] == "parsed"
    suggestions = " ".join(body["suggested_actions"]).lower()
    assert "upload your resume" not in suggestions


def test_dashboard_includes_mock_interview_stats(client):
    headers = _auth_headers(client)
    session = client.post("/api/v1/interviews/sessions", headers=headers, json={"question_count": 3}).json()["data"]
    client.post(
        f"/api/v1/interviews/sessions/{session['id']}/answers",
        headers=headers,
        json={"question_id": session["questions"][0]["id"], "answer_text": "A reasonably detailed answer here."},
    )

    response = client.get("/api/v1/dashboard", headers=headers)
    body = response.json()["data"]
    assert body["interview_stats"]["total_sessions"] == 1
    assert body["interview_stats"]["completed_sessions"] == 0
    assert body["interview_stats"]["average_score"] is not None
    suggestions = " ".join(body["suggested_actions"]).lower()
    assert "mock interview" not in suggestions


def test_dashboard_data_is_isolated_per_student(client):
    headers_a = _auth_headers(client, STUDENT_A)
    _add_skill(client, headers_a, "Python")

    other_student = {"email": "bikash@example.edu.np", "password": "password123", "full_name": "Bikash Sainju"}
    headers_b = _auth_headers(client, other_student)
    response = client.get("/api/v1/dashboard", headers=headers_b)
    assert response.json()["data"]["skill_count"] == 0


# --- profile completion unit tests (no HTTP needed) -------------------------


class _FakeProfile:
    def __init__(self, **overrides):
        self.university = None
        self.degree = None
        self.semester = None
        self.bio = None
        self.github_url = None
        self.linkedin_url = None
        self.portfolio_url = None
        self.skills = []
        self.projects = []
        self.experiences = []
        self.certifications = []
        self.resumes = []
        for key, value in overrides.items():
            setattr(self, key, value)


def test_compute_profile_completion_empty_profile_scores_zero():
    result = compute_profile_completion(_FakeProfile())
    assert result.score == 0
    assert all(not item.done for item in result.checklist)


def test_compute_profile_completion_full_profile_scores_100():
    result = compute_profile_completion(
        _FakeProfile(
            university="St. Xavier's",
            degree="BSc. CSIT",
            semester=6,
            bio="A bio",
            github_url="https://github.com/asha",
            skills=[object(), object(), object()],
            projects=[object()],
            experiences=[object()],
            certifications=[object()],
            resumes=[object()],
        )
    )
    assert result.score == 100
