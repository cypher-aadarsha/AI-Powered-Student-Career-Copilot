"""Coverage for Phase 7's learning-resources module: browsing, the
skill_id filter, and the skill-gap-driven `/careers/{id}/learning-plan`
endpoint that ties this module to Phase 6's career matching.
"""
import pytest

from seed.career_roles import seed_career_roles
from seed.learning_resources import RESOURCES, seed_learning_resources

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}


@pytest.fixture(autouse=True)
def _seed_catalogue(db_session):
    seed_career_roles(db_session)
    seed_learning_resources(db_session)


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _find_role_id(client, headers, title: str) -> str:
    response = client.get("/api/v1/careers", headers=headers)
    match = next(item for item in response.json()["data"] if item["role"]["title"] == title)
    return match["role"]["id"]


def _find_skill_id(client, headers, name: str) -> str:
    response = client.get("/api/v1/learning-resources", headers=headers)
    for resource in response.json()["data"]:
        for skill in resource["skills"]:
            if skill["name"] == name:
                return skill["id"]
    raise AssertionError(f"No seeded resource references skill {name!r}")


def test_list_learning_resources_without_auth_returns_401(client):
    assert client.get("/api/v1/learning-resources").status_code == 401


def test_list_learning_resources_returns_every_seeded_resource(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/learning-resources", headers=headers)
    assert response.status_code == 200
    titles = {item["title"] for item in response.json()["data"]}
    assert titles == {resource[0] for resource in RESOURCES}


def test_list_learning_resources_filtered_by_skill(client):
    headers = _auth_headers(client)
    skill_id = _find_skill_id(client, headers, "Python")

    response = client.get(f"/api/v1/learning-resources?skill_id={skill_id}", headers=headers)
    assert response.status_code == 200
    titles = {item["title"] for item in response.json()["data"]}
    assert "The Python Tutorial" in titles
    assert "Real Python" in titles
    assert "Learn React" not in titles


def test_get_learning_resource_detail(client):
    headers = _auth_headers(client)
    listing = client.get("/api/v1/learning-resources", headers=headers).json()["data"]
    resource_id = next(item["id"] for item in listing if item["title"] == "Git Documentation")

    response = client.get(f"/api/v1/learning-resources/{resource_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["provider"] == "Git"
    assert body["resource_type"] == "documentation"
    assert {skill["name"] for skill in body["skills"]} == {"Git"}


def test_get_learning_resource_for_unknown_id_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/learning-resources/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


def test_role_learning_plan_lists_resources_for_missing_required_skills(client):
    headers = _auth_headers(client)
    role_id = _find_role_id(client, headers, "Backend Developer")

    response = client.get(f"/api/v1/careers/{role_id}/learning-plan", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["role"]["title"] == "Backend Developer"

    required_skills = {entry["skill"]["name"] for entry in body["missing_required"]}
    assert required_skills == {"Python", "SQL", "REST APIs", "Git"}

    python_entry = next(e for e in body["missing_required"] if e["skill"]["name"] == "Python")
    resource_titles = {r["title"] for r in python_entry["resources"]}
    assert "The Python Tutorial" in resource_titles
    assert "Real Python" in resource_titles


def test_role_learning_plan_has_no_missing_skills_once_a_student_has_them_all(client):
    headers = _auth_headers(client)
    for skill in ("Python", "SQL", "REST APIs", "Git", "Docker", "PostgreSQL", "FastAPI"):
        assert (
            client.post(
                "/api/v1/profile/skills",
                headers=headers,
                json={"name": skill, "category": "technical", "proficiency_level": "expert"},
            ).status_code
            == 201
        )
    role_id = _find_role_id(client, headers, "Backend Developer")

    response = client.get(f"/api/v1/careers/{role_id}/learning-plan", headers=headers)
    body = response.json()["data"]
    assert body["missing_required"] == []
    assert body["missing_preferred"] == []


def test_role_learning_plan_for_unknown_role_returns_404(client):
    headers = _auth_headers(client)
    response = client.get(
        "/api/v1/careers/00000000-0000-0000-0000-000000000000/learning-plan", headers=headers
    )
    assert response.status_code == 404


def test_seed_learning_resources_is_idempotent(db_session):
    first_run = seed_learning_resources(db_session)
    second_run = seed_learning_resources(db_session)
    assert first_run == 0  # already seeded by the autouse fixture
    assert second_run == 0
