"""Coverage for Phase 10: admin-only CRUD over the four platform-curated
catalogues (career roles, learning resources, job postings, interview
questions), user moderation, role-guard enforcement, and the admin-
provisioning seed script.
"""
import uuid

from app.core.security import hash_password
from app.models.mock_interview import MockInterviewSession, MockInterviewSessionQuestion
from app.models.user import UserRole
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from seed.create_admin import DEFAULT_ADMIN_EMAIL, create_admin

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}
ADMIN_A = {"email": "admin@example.edu.np", "password": "admin-password-1", "full_name": "Admin One"}


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _admin_headers(client, db_session, user=ADMIN_A) -> dict:
    UserRepository(db_session).create(
        email=user["email"], password_hash=hash_password(user["password"]), full_name=user["full_name"], role=UserRole.admin
    )
    db_session.flush()
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- role guard ----------------------------------------------------------


def test_admin_routes_require_auth(client):
    assert client.get("/api/v1/admin/ping").status_code == 401


def test_admin_routes_are_forbidden_for_a_student(client):
    headers = _auth_headers(client)
    for path in (
        "/api/v1/admin/ping",
        "/api/v1/admin/users",
        "/api/v1/admin/career-roles",
        "/api/v1/admin/learning-resources",
        "/api/v1/admin/job-postings",
        "/api/v1/admin/interview-questions",
    ):
        assert client.get(path, headers=headers).status_code == 403


def test_admin_ping_succeeds_for_an_admin(client, db_session):
    headers = _admin_headers(client, db_session)
    assert client.get("/api/v1/admin/ping", headers=headers).status_code == 200


# --- users ---------------------------------------------------------------


def test_admin_can_list_and_deactivate_and_reactivate_a_user(client, db_session):
    admin_headers = _admin_headers(client, db_session)
    student_headers = _auth_headers(client)
    student_id = client.get("/api/v1/users/me", headers=student_headers).json()["data"]["id"]

    listing = client.get("/api/v1/admin/users", headers=admin_headers)
    assert listing.status_code == 200
    emails = {u["email"] for u in listing.json()["data"]}
    assert STUDENT_A["email"] in emails
    assert ADMIN_A["email"] in emails

    deactivate = client.patch(f"/api/v1/admin/users/{student_id}", headers=admin_headers, json={"is_active": False})
    assert deactivate.status_code == 200
    assert deactivate.json()["data"]["is_active"] is False

    # a deactivated user can no longer log in
    blocked = client.post("/api/v1/auth/login", json={"email": STUDENT_A["email"], "password": STUDENT_A["password"]})
    assert blocked.status_code == 403

    reactivate = client.patch(f"/api/v1/admin/users/{student_id}", headers=admin_headers, json={"is_active": True})
    assert reactivate.json()["data"]["is_active"] is True
    assert client.post(
        "/api/v1/auth/login", json={"email": STUDENT_A["email"], "password": STUDENT_A["password"]}
    ).status_code == 200


def test_admin_cannot_deactivate_their_own_account(client, db_session):
    admin_headers = _admin_headers(client, db_session)
    admin_id = client.get("/api/v1/users/me", headers=admin_headers).json()["data"]["id"]
    response = client.patch(f"/api/v1/admin/users/{admin_id}", headers=admin_headers, json={"is_active": False})
    assert response.status_code == 400


# --- career roles ----------------------------------------------------------


def test_admin_career_role_crud(client, db_session):
    headers = _admin_headers(client, db_session)

    create = client.post(
        "/api/v1/admin/career-roles",
        headers=headers,
        json={
            "title": "Platform Engineer",
            "description": "Builds internal developer platforms.",
            "required_skills": [{"name": "Kubernetes", "category": "tool"}],
            "preferred_skills": [{"name": "Go", "category": "programming_language"}],
        },
    )
    assert create.status_code == 201
    role = create.json()["data"]
    assert role["title"] == "Platform Engineer"
    assert {s["name"] for s in role["required_skills"]} == {"Kubernetes"}
    assert {s["name"] for s in role["preferred_skills"]} == {"Go"}

    listing = client.get("/api/v1/admin/career-roles", headers=headers)
    assert any(r["id"] == role["id"] for r in listing.json()["data"])

    update = client.put(
        f"/api/v1/admin/career-roles/{role['id']}",
        headers=headers,
        json={
            "title": "Platform Engineer",
            "description": "Updated description.",
            "required_skills": [{"name": "Kubernetes", "category": "tool"}, {"name": "Terraform", "category": "tool"}],
            "preferred_skills": [],
        },
    )
    assert update.status_code == 200
    assert update.json()["data"]["description"] == "Updated description."
    assert {s["name"] for s in update.json()["data"]["required_skills"]} == {"Kubernetes", "Terraform"}
    assert update.json()["data"]["preferred_skills"] == []

    delete = client.delete(f"/api/v1/admin/career-roles/{role['id']}", headers=headers)
    assert delete.status_code == 204
    assert client.get("/api/v1/admin/career-roles", headers=headers).json()["data"] == []


def test_admin_career_role_title_must_be_unique(client, db_session):
    headers = _admin_headers(client, db_session)
    payload = {"title": "Duplicate Role", "description": None, "required_skills": [], "preferred_skills": []}
    assert client.post("/api/v1/admin/career-roles", headers=headers, json=payload).status_code == 201
    conflict = client.post("/api/v1/admin/career-roles", headers=headers, json=payload)
    assert conflict.status_code == 409


def test_admin_career_role_update_for_unknown_id_returns_404(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.put(
        "/api/v1/admin/career-roles/00000000-0000-0000-0000-000000000000",
        headers=headers,
        json={"title": "X", "description": None, "required_skills": [], "preferred_skills": []},
    )
    assert response.status_code == 404


def test_admin_career_role_reuses_existing_skill_case_insensitively(client, db_session):
    headers = _admin_headers(client, db_session)
    client.post(
        "/api/v1/admin/career-roles",
        headers=headers,
        json={"title": "Role A", "description": None, "required_skills": [{"name": "Python", "category": "programming_language"}], "preferred_skills": []},
    )
    second = client.post(
        "/api/v1/admin/career-roles",
        headers=headers,
        json={"title": "Role B", "description": None, "required_skills": [{"name": "python", "category": "programming_language"}], "preferred_skills": []},
    ).json()["data"]
    first = next(r for r in client.get("/api/v1/admin/career-roles", headers=headers).json()["data"] if r["title"] == "Role A")
    assert first["required_skills"][0]["id"] == second["required_skills"][0]["id"]


# --- learning resources ------------------------------------------------------


def test_admin_learning_resource_crud(client, db_session):
    headers = _admin_headers(client, db_session)

    create = client.post(
        "/api/v1/admin/learning-resources",
        headers=headers,
        json={
            "title": "Kubernetes Basics",
            "description": "An intro course.",
            "url": "https://kubernetes.io/docs/tutorials/",
            "provider": "Kubernetes",
            "resource_type": "course",
            "skills": [{"name": "Kubernetes", "category": "tool"}],
        },
    )
    assert create.status_code == 201
    resource = create.json()["data"]
    assert resource["title"] == "Kubernetes Basics"
    assert {s["name"] for s in resource["skills"]} == {"Kubernetes"}

    update = client.put(
        f"/api/v1/admin/learning-resources/{resource['id']}",
        headers=headers,
        json={
            "title": "Kubernetes Basics (Updated)",
            "description": "An intro course.",
            "url": "https://kubernetes.io/docs/tutorials/",
            "provider": "Kubernetes",
            "resource_type": "documentation",
            "skills": [],
        },
    )
    assert update.status_code == 200
    assert update.json()["data"]["title"] == "Kubernetes Basics (Updated)"
    assert update.json()["data"]["resource_type"] == "documentation"
    assert update.json()["data"]["skills"] == []

    delete = client.delete(f"/api/v1/admin/learning-resources/{resource['id']}", headers=headers)
    assert delete.status_code == 204
    assert client.get(f"/api/v1/learning-resources/{resource['id']}", headers=headers).status_code == 404


def test_admin_learning_resource_update_for_unknown_id_returns_404(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.put(
        "/api/v1/admin/learning-resources/00000000-0000-0000-0000-000000000000",
        headers=headers,
        json={"title": "X", "description": None, "url": "https://example.com", "provider": "P", "resource_type": "article", "skills": []},
    )
    assert response.status_code == 404


# --- job postings ------------------------------------------------------------


def test_admin_job_posting_crud(client, db_session):
    headers = _admin_headers(client, db_session)

    create = client.post(
        "/api/v1/admin/job-postings",
        headers=headers,
        json={
            "title": "Platform Engineer",
            "company": "Acme Cloud",
            "location": "Remote",
            "employment_type": "full_time",
            "is_remote": True,
            "description": "Own the internal platform.",
            "apply_url": "https://example.com/careers/acme-platform-engineer",
            "skills": [{"name": "Kubernetes", "category": "tool"}],
        },
    )
    assert create.status_code == 201
    job = create.json()["data"]
    assert job["company"] == "Acme Cloud"
    assert {s["name"] for s in job["skills"]} == {"Kubernetes"}

    update = client.put(
        f"/api/v1/admin/job-postings/{job['id']}",
        headers=headers,
        json={
            "title": "Senior Platform Engineer",
            "company": "Acme Cloud",
            "location": "Remote",
            "employment_type": "contract",
            "is_remote": True,
            "description": "Own the internal platform.",
            "apply_url": "https://example.com/careers/acme-platform-engineer",
            "skills": [],
        },
    )
    assert update.status_code == 200
    assert update.json()["data"]["title"] == "Senior Platform Engineer"
    assert update.json()["data"]["employment_type"] == "contract"

    delete = client.delete(f"/api/v1/admin/job-postings/{job['id']}", headers=headers)
    assert delete.status_code == 204
    assert client.get(f"/api/v1/jobs/{job['id']}", headers=headers).status_code == 404


def test_admin_job_posting_update_for_unknown_id_returns_404(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.put(
        "/api/v1/admin/job-postings/00000000-0000-0000-0000-000000000000",
        headers=headers,
        json={
            "title": "X", "company": "Y", "location": "Z", "employment_type": "full_time",
            "is_remote": False, "description": None, "apply_url": "https://example.com", "skills": [],
        },
    )
    assert response.status_code == 404


# --- interview questions ------------------------------------------------------


def test_admin_interview_question_crud(client, db_session):
    headers = _admin_headers(client, db_session)

    create = client.post(
        "/api/v1/admin/interview-questions",
        headers=headers,
        json={
            "question_text": "What is a Kubernetes pod?",
            "category": "technical",
            "difficulty": "easy",
            "model_answer": "The smallest deployable unit, wrapping one or more containers.",
            "skills": [{"name": "Kubernetes", "category": "tool"}],
        },
    )
    assert create.status_code == 201
    question = create.json()["data"]
    assert question["model_answer"]
    assert {s["name"] for s in question["skills"]} == {"Kubernetes"}

    update = client.put(
        f"/api/v1/admin/interview-questions/{question['id']}",
        headers=headers,
        json={
            "question_text": "What is a Kubernetes pod, in detail?",
            "category": "technical",
            "difficulty": "medium",
            "model_answer": "Updated answer.",
            "skills": [],
        },
    )
    assert update.status_code == 200
    assert update.json()["data"]["difficulty"] == "medium"
    assert update.json()["data"]["skills"] == []

    delete = client.delete(f"/api/v1/admin/interview-questions/{question['id']}", headers=headers)
    assert delete.status_code == 204


def test_admin_cannot_delete_an_interview_question_already_used_in_a_session(client, db_session):
    headers = _admin_headers(client, db_session)
    question = client.post(
        "/api/v1/admin/interview-questions",
        headers=headers,
        json={"question_text": "Used question", "category": "behavioral", "difficulty": "easy", "model_answer": None, "skills": []},
    ).json()["data"]

    student_headers = _auth_headers(client)
    user_id = uuid.UUID(client.get("/api/v1/users/me", headers=student_headers).json()["data"]["id"])
    profile = ProfileRepository(db_session).get_by_user_id(user_id)
    if profile is None:
        profile = ProfileRepository(db_session).create(user_id=user_id)
    session = MockInterviewSession(student_profile_id=profile.id)
    db_session.add(session)
    db_session.flush()
    db_session.add(MockInterviewSessionQuestion(session_id=session.id, question_id=uuid.UUID(question["id"]), order_index=0))
    db_session.flush()

    response = client.delete(f"/api/v1/admin/interview-questions/{question['id']}", headers=headers)
    assert response.status_code == 409


# --- seed script -----------------------------------------------------------


def test_create_admin_seed_script_is_idempotent(db_session):
    first = create_admin(db_session, email="seeded-admin@example.edu.np", password="password123", full_name="Seeded Admin")
    second = create_admin(db_session, email="seeded-admin@example.edu.np", password="password123", full_name="Seeded Admin")
    assert first is True
    assert second is False
    user = UserRepository(db_session).get_by_email("seeded-admin@example.edu.np")
    assert user.role == UserRole.admin


def test_create_admin_default_email_can_actually_log_in(client, db_session):
    # Regression test: the script's default email must pass the app's own
    # EmailStr validation at /auth/login, the same schema used for every
    # other login — an email that only the repository-level bypass accepts
    # would create an admin account nobody could actually use.
    create_admin(db_session, email=DEFAULT_ADMIN_EMAIL, password="admin-password-1", full_name="Platform Admin")
    response = client.post("/api/v1/auth/login", json={"email": DEFAULT_ADMIN_EMAIL, "password": "admin-password-1"})
    assert response.status_code == 200
