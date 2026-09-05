"""Coverage for Phase 4: profile core fields, skills, projects, experiences,
certifications — including normalization (case-insensitive skill dedupe),
validation (date ordering, URL format), and cross-user ownership checks.
"""
import pytest

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}
STUDENT_B = {"email": "bikash@example.edu.np", "password": "password123", "full_name": "Bikash Sainju"}


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- profile core -------------------------------------------------------


def test_get_profile_lazily_creates_an_empty_profile(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["university"] is None
    assert body["skills"] == []
    assert body["projects"] == []
    assert body["experiences"] == []
    assert body["certifications"] == []


def test_get_profile_without_auth_returns_401(client):
    response = client.get("/api/v1/profile")
    assert response.status_code == 401


def test_put_profile_updates_core_fields(client):
    headers = _auth_headers(client)
    response = client.put(
        "/api/v1/profile",
        headers=headers,
        json={
            "university": "St. Xavier's College",
            "degree": "BSc. CSIT",
            "semester": 6,
            "graduation_year": 2027,
            "location": "Kathmandu, Nepal",
            "bio": "Aspiring backend engineer.",
            "github_url": "https://github.com/asha",
            "linkedin_url": None,
            "portfolio_url": None,
            "profile_picture_url": None,
        },
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["university"] == "St. Xavier's College"
    assert body["semester"] == 6
    assert body["github_url"] == "https://github.com/asha"


def test_put_profile_rejects_out_of_range_semester(client):
    headers = _auth_headers(client)
    response = client.put("/api/v1/profile", headers=headers, json={"semester": 99})
    assert response.status_code == 422


def test_put_profile_rejects_a_malformed_url(client):
    headers = _auth_headers(client)
    response = client.put("/api/v1/profile", headers=headers, json={"github_url": "not-a-url"})
    assert response.status_code == 422


# --- skills ---------------------------------------------------------------


def test_add_skill_creates_and_attaches_a_catalogue_entry(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": "React", "category": "framework", "proficiency_level": "intermediate"},
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["skill"]["name"] == "React"
    assert body["proficiency_level"] == "intermediate"
    assert body["source"] == "manual"


def test_add_skill_normalizes_case_insensitively_and_rejects_exact_duplicate(client):
    headers = _auth_headers(client)
    client.post(
        "/api/v1/profile/skills", headers=headers, json={"name": "React", "category": "framework"}
    )
    # Same skill, different casing -> resolves to the same catalogue row -> conflict.
    response = client.post(
        "/api/v1/profile/skills", headers=headers, json={"name": "react", "category": "framework"}
    )
    assert response.status_code == 409


def test_remove_skill(client):
    headers = _auth_headers(client)
    add = client.post(
        "/api/v1/profile/skills", headers=headers, json={"name": "Docker", "category": "tool"}
    )
    student_skill_id = add.json()["data"]["id"]
    response = client.delete(f"/api/v1/profile/skills/{student_skill_id}", headers=headers)
    assert response.status_code == 204

    profile = client.get("/api/v1/profile", headers=headers).json()["data"]
    assert profile["skills"] == []


def test_cannot_remove_another_students_skill(client):
    headers_a = _auth_headers(client, STUDENT_A)
    add = client.post(
        "/api/v1/profile/skills", headers=headers_a, json={"name": "Kubernetes", "category": "tool"}
    )
    student_skill_id = add.json()["data"]["id"]

    headers_b = _auth_headers(client, STUDENT_B)
    response = client.delete(f"/api/v1/profile/skills/{student_skill_id}", headers=headers_b)
    assert response.status_code == 404


# --- projects ---------------------------------------------------------------


def test_add_project_with_tagged_skills(client):
    headers = _auth_headers(client)
    skill = client.post(
        "/api/v1/profile/skills", headers=headers, json={"name": "PostgreSQL", "category": "tool"}
    ).json()["data"]["skill"]

    response = client.post(
        "/api/v1/profile/projects",
        headers=headers,
        json={
            "title": "Career Copilot",
            "description": "A career readiness platform.",
            "repo_url": "https://github.com/asha/career-copilot",
            "skill_ids": [skill["id"]],
            "start_date": "2026-01-01",
        },
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["title"] == "Career Copilot"
    assert [s["id"] for s in body["skills"]] == [skill["id"]]


def test_project_end_date_before_start_date_is_rejected(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/profile/projects",
        headers=headers,
        json={"title": "Bad dates", "start_date": "2026-06-01", "end_date": "2026-01-01"},
    )
    assert response.status_code == 422


def test_update_and_delete_project(client):
    headers = _auth_headers(client)
    created = client.post(
        "/api/v1/profile/projects", headers=headers, json={"title": "Draft title"}
    ).json()["data"]

    updated = client.put(
        f"/api/v1/profile/projects/{created['id']}",
        headers=headers,
        json={"title": "Final title", "description": "Updated."},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["title"] == "Final title"

    deleted = client.delete(f"/api/v1/profile/projects/{created['id']}", headers=headers)
    assert deleted.status_code == 204


def test_cannot_update_another_students_project(client):
    headers_a = _auth_headers(client, STUDENT_A)
    project = client.post(
        "/api/v1/profile/projects", headers=headers_a, json={"title": "Private project"}
    ).json()["data"]

    headers_b = _auth_headers(client, STUDENT_B)
    response = client.put(
        f"/api/v1/profile/projects/{project['id']}", headers=headers_b, json={"title": "Hijacked"}
    )
    assert response.status_code == 404


# --- experiences ------------------------------------------------------------


def test_add_update_delete_experience(client):
    headers = _auth_headers(client)
    created = client.post(
        "/api/v1/profile/experiences",
        headers=headers,
        json={
            "title": "Backend Intern",
            "company": "Some Startup",
            "employment_type": "internship",
            "start_date": "2026-06-01",
            "is_current": True,
        },
    )
    assert created.status_code == 201
    experience_id = created.json()["data"]["id"]

    updated = client.put(
        f"/api/v1/profile/experiences/{experience_id}",
        headers=headers,
        json={
            "title": "Backend Engineer Intern",
            "company": "Some Startup",
            "employment_type": "internship",
            "start_date": "2026-06-01",
            "is_current": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["title"] == "Backend Engineer Intern"

    deleted = client.delete(f"/api/v1/profile/experiences/{experience_id}", headers=headers)
    assert deleted.status_code == 204


# --- certifications ---------------------------------------------------------


def test_add_update_delete_certification(client):
    headers = _auth_headers(client)
    created = client.post(
        "/api/v1/profile/certifications",
        headers=headers,
        json={"name": "AWS Cloud Practitioner", "issuer": "AWS", "issue_date": "2026-03-01"},
    )
    assert created.status_code == 201
    cert_id = created.json()["data"]["id"]

    updated = client.put(
        f"/api/v1/profile/certifications/{cert_id}",
        headers=headers,
        json={"name": "AWS Certified Cloud Practitioner", "issuer": "AWS"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "AWS Certified Cloud Practitioner"

    deleted = client.delete(f"/api/v1/profile/certifications/{cert_id}", headers=headers)
    assert deleted.status_code == 204


def test_full_profile_aggregates_everything(client):
    headers = _auth_headers(client)
    client.put("/api/v1/profile", headers=headers, json={"university": "St. Xavier's College"})
    client.post("/api/v1/profile/skills", headers=headers, json={"name": "Python", "category": "programming_language"})
    client.post("/api/v1/profile/projects", headers=headers, json={"title": "A project"})
    client.post(
        "/api/v1/profile/experiences",
        headers=headers,
        json={
            "title": "Intern",
            "company": "Co",
            "employment_type": "internship",
            "start_date": "2026-01-01",
            "is_current": False,
            "end_date": "2026-04-01",
        },
    )
    client.post("/api/v1/profile/certifications", headers=headers, json={"name": "A cert"})

    profile = client.get("/api/v1/profile", headers=headers).json()["data"]
    assert profile["university"] == "St. Xavier's College"
    assert len(profile["skills"]) == 1
    assert len(profile["projects"]) == 1
    assert len(profile["experiences"]) == 1
    assert len(profile["certifications"]) == 1
