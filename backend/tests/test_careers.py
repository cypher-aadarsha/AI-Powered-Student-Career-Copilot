"""Coverage for Phase 6: the career-role catalogue, the explainable
skill-gap scoring formula, and the ranked-recommendations/detail endpoints.

Every test that needs roles in the database seeds them via
`seed_career_roles` directly against the test's `db_session` — the same
session `client`'s overridden `get_db` yields, so uncommitted rows are
visible to requests made through `client` in the same test.
"""
import uuid

import pytest

from app.models.skill import Skill, SkillCategory
from app.models.student_skill import ProficiencyLevel
from app.services.skill_gap import compute_skill_gap
from seed.career_roles import ROLES, seed_career_roles


def _skill(name: str) -> Skill:
    return Skill(id=uuid.uuid4(), name=name, category=SkillCategory.technical)

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}
STUDENT_B = {"email": "bikash@example.edu.np", "password": "password123", "full_name": "Bikash Sainju"}


@pytest.fixture(autouse=True)
def _seed_roles(db_session):
    seed_career_roles(db_session)


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_skill(client, headers, name: str, proficiency: str = "beginner") -> None:
    response = client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": name, "category": "technical", "proficiency_level": proficiency},
    )
    assert response.status_code == 201


def _find_role_id(client, headers, title: str) -> str:
    response = client.get("/api/v1/careers", headers=headers)
    match = next(item for item in response.json()["data"] if item["role"]["title"] == title)
    return match["role"]["id"]


# --- endpoints -------------------------------------------------------------


def test_list_careers_without_auth_returns_401(client):
    assert client.get("/api/v1/careers").status_code == 401


def test_list_careers_returns_every_seeded_role(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/careers", headers=headers)
    assert response.status_code == 200
    titles = {item["role"]["title"] for item in response.json()["data"]}
    assert titles == {role["title"] for role in ROLES}


def test_student_with_no_skills_scores_zero_on_every_role(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/careers", headers=headers)
    assert all(item["score"] == 0 for item in response.json()["data"])
    assert all(item["matched_required"] == 0 for item in response.json()["data"])


def test_backend_role_ranks_first_for_a_backend_leaning_student(client):
    headers = _auth_headers(client)
    for skill in ("Python", "SQL", "REST APIs", "Git", "Docker", "PostgreSQL", "FastAPI"):
        _add_skill(client, headers, skill, proficiency="expert")

    response = client.get("/api/v1/careers", headers=headers)
    ranked = response.json()["data"]
    assert ranked[0]["role"]["title"] == "Backend Developer"
    assert ranked[0]["score"] == 100
    # descending order is preserved for the rest of the list
    scores = [item["score"] for item in ranked]
    assert scores == sorted(scores, reverse=True)


def test_career_detail_lists_matched_and_missing_skills(client):
    headers = _auth_headers(client)
    for skill in ("Python", "SQL", "REST APIs", "Git"):
        _add_skill(client, headers, skill, proficiency="beginner")
    role_id = _find_role_id(client, headers, "Backend Developer")

    response = client.get(f"/api/v1/careers/{role_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["score"] == 36  # 4 required skills at "beginner" (0.5x) = 8*0.5=4 / 11 possible = 36%
    matched_names = {m["skill"]["name"] for m in body["matched_skills"]}
    assert matched_names == {"Python", "SQL", "REST APIs", "Git"}
    assert body["missing_required_skills"] == []
    missing_preferred = {s["name"] for s in body["missing_preferred_skills"]}
    assert missing_preferred == {"Docker", "PostgreSQL", "FastAPI"}
    assert "36/100" in body["summary"]


def test_career_detail_for_unknown_role_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/careers/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


def test_career_scores_are_isolated_per_student(client):
    headers_a = _auth_headers(client, STUDENT_A)
    for skill in ("Python", "SQL", "REST APIs", "Git"):
        _add_skill(client, headers_a, skill, proficiency="expert")

    headers_b = _auth_headers(client, STUDENT_B)
    role_id = _find_role_id(client, headers_b, "Backend Developer")
    response = client.get(f"/api/v1/careers/{role_id}", headers=headers_b)
    assert response.json()["data"]["score"] == 0


# --- seed idempotency --------------------------------------------------------


def test_seed_career_roles_is_idempotent(db_session):
    first_run = seed_career_roles(db_session)
    second_run = seed_career_roles(db_session)
    assert first_run == 0  # already seeded by the autouse fixture
    assert second_run == 0


# --- skill-gap scoring unit tests (no HTTP/DB needed) -----------------------


def test_compute_skill_gap_full_match_scores_100():
    python, sql = _skill("Python"), _skill("SQL")
    result = compute_skill_gap(
        student_skills={python.id: ProficiencyLevel.expert, sql.id: ProficiencyLevel.expert},
        required_skills=[python, sql],
        preferred_skills=[],
    )
    assert result.score == 100
    assert result.missing_required == []


def test_compute_skill_gap_no_match_scores_zero():
    python, sql = _skill("Python"), _skill("SQL")
    result = compute_skill_gap(student_skills={}, required_skills=[python, sql], preferred_skills=[])
    assert result.score == 0
    assert {s.name for s in result.missing_required} == {"Python", "SQL"}


def test_compute_skill_gap_rewards_higher_proficiency():
    python = _skill("Python")
    beginner = compute_skill_gap({python.id: ProficiencyLevel.beginner}, [python], [])
    expert = compute_skill_gap({python.id: ProficiencyLevel.expert}, [python], [])
    assert expert.score > beginner.score


def test_compute_skill_gap_weighs_required_above_preferred():
    required_skill = _skill("Python")
    preferred_skill = _skill("Docker")
    has_required = compute_skill_gap(
        {required_skill.id: ProficiencyLevel.intermediate}, [required_skill], [preferred_skill]
    )
    has_preferred = compute_skill_gap(
        {preferred_skill.id: ProficiencyLevel.intermediate}, [required_skill], [preferred_skill]
    )
    assert has_required.score > has_preferred.score
