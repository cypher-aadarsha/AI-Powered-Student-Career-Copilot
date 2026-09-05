"""Unit + integration coverage for Phase 3: registration, login, JWT-gated
routes, and role-based authorization — the exact flows FR-01..FR-04 promise.
"""
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository

VALID_REGISTRATION = {
    "email": "asha.sharma@example.edu.np",
    "password": "correct-horse-battery",
    "full_name": "Asha Sharma",
}


# --- unit: password hashing --------------------------------------------------


def test_hash_password_is_not_the_plaintext_and_verifies_correctly():
    hashed = hash_password("s3cret-passphrase")
    assert hashed != "s3cret-passphrase"
    assert verify_password("s3cret-passphrase", hashed)
    assert not verify_password("wrong-passphrase", hashed)


# --- integration: registration -----------------------------------------------


def test_register_creates_a_student_account_and_never_returns_the_password(client):
    response = client.post("/api/v1/auth/register", json=VALID_REGISTRATION)
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["email"] == VALID_REGISTRATION["email"]
    assert body["role"] == "student"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejects_a_password_below_the_minimum_length(client):
    response = client.post(
        "/api/v1/auth/register", json={**VALID_REGISTRATION, "password": "short"}
    )
    assert response.status_code == 422


def test_register_rejects_a_duplicate_email(client):
    client.post("/api/v1/auth/register", json=VALID_REGISTRATION)
    response = client.post("/api/v1/auth/register", json=VALID_REGISTRATION)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


# --- integration: login ------------------------------------------------------


def test_login_with_correct_credentials_returns_a_bearer_token(client):
    client.post("/api/v1/auth/register", json=VALID_REGISTRATION)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_REGISTRATION["email"], "password": VALID_REGISTRATION["password"]},
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_returns_401_with_a_generic_message(client):
    client.post("/api/v1/auth/register", json=VALID_REGISTRATION)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_REGISTRATION["email"], "password": "totally-wrong"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password."


def test_login_for_an_unknown_email_returns_the_same_401(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.edu.np", "password": "whatever123"}
    )
    assert response.status_code == 401


# --- integration: protected routes / RBAC ------------------------------------


def _register_and_login(client) -> str:
    client.post("/api/v1/auth/register", json=VALID_REGISTRATION)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_REGISTRATION["email"], "password": VALID_REGISTRATION["password"]},
    )
    return response.json()["data"]["access_token"]


def test_me_without_a_token_returns_401(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_me_with_a_valid_token_returns_the_current_user(client):
    token = _register_and_login(client)
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["data"]["email"] == VALID_REGISTRATION["email"]


def test_me_with_a_garbage_token_returns_401_not_500(client):
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer not-a-real-jwt"})
    assert response.status_code == 401


def test_admin_route_is_forbidden_for_a_student(client):
    token = _register_and_login(client)
    response = client.get("/api/v1/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_route_is_allowed_for_an_admin(client, db_session: Session):
    # Admin accounts are provisioned out-of-band (never via self-registration,
    # see AuthService.register) — created directly here to prove the guard
    # itself, not the (deliberately unbuilt) provisioning path.
    UserRepository(db_session).create(
        email="admin@example.edu.np",
        password_hash=hash_password("admin-password-1"),
        full_name="Platform Admin",
        role=UserRole.admin,
    )
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.edu.np", "password": "admin-password-1"}
    )
    token = login_response.json()["data"]["access_token"]

    response = client.get("/api/v1/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
