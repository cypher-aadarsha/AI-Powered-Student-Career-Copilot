"""Coverage for Phase 11: defensive HTTP headers, brute-force rate limiting
on auth endpoints, and adversarial-input handling (tampered/expired JWTs,
injection-style strings) that isn't tied to any single feature module.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings
from app.core.security import create_access_token

STUDENT = {"email": "hardening@example.edu.np", "password": "password123", "full_name": "Hardening Test"}


def _register_and_login(client, user=STUDENT) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- security headers --------------------------------------------------


def test_every_response_carries_defensive_headers(client):
    response = client.get("/api/v1/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "permissions-policy" in response.headers


def test_hsts_is_not_sent_outside_production(client):
    # ENVIRONMENT defaults to "development" in tests — sending HSTS over a
    # connection that isn't actually HTTPS-terminated would be misleading.
    response = client.get("/api/v1/health")
    assert "strict-transport-security" not in response.headers


# --- rate limiting -------------------------------------------------------


def test_login_is_rate_limited_after_repeated_attempts(client):
    client.post("/api/v1/auth/register", json=STUDENT)
    for _ in range(20):
        response = client.post(
            "/api/v1/auth/login", json={"email": STUDENT["email"], "password": "wrong-password"}
        )
        assert response.status_code == 401

    limited = client.post("/api/v1/auth/login", json={"email": STUDENT["email"], "password": "wrong-password"})
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "too_many_requests"

    # Even the *correct* password is blocked while the window is exhausted —
    # the limiter counts requests, not failures, so it can't be used to
    # distinguish a real password from a wrong one.
    still_limited = client.post(
        "/api/v1/auth/login", json={"email": STUDENT["email"], "password": STUDENT["password"]}
    )
    assert still_limited.status_code == 429


def test_register_is_rate_limited_after_repeated_attempts(client):
    for i in range(20):
        client.post(
            "/api/v1/auth/register",
            json={"email": f"flood{i}@example.edu.np", "password": "password123", "full_name": "Flood Test"},
        )

    limited = client.post(
        "/api/v1/auth/register",
        json={"email": "flood-final@example.edu.np", "password": "password123", "full_name": "Flood Test"},
    )
    assert limited.status_code == 429


# --- JWT tampering / expiry ----------------------------------------------


def test_expired_token_is_rejected(client):
    settings = get_settings()
    register = client.post("/api/v1/auth/register", json=STUDENT)
    user_id = register.json()["data"]["id"]

    expired_token = create_access_token(
        subject=user_id,
        role="student",
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_minutes=-1,
    )
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_token_signed_with_the_wrong_secret_is_rejected(client):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    forged_token = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000000", "role": "admin", "iat": now, "exp": now + timedelta(minutes=5)},
        "not-the-real-secret",
        algorithm=settings.jwt_algorithm,
    )
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {forged_token}"})
    assert response.status_code == 401


def test_token_with_a_tampered_payload_is_rejected(client):
    headers = _register_and_login(client)
    token = headers["Authorization"].removeprefix("Bearer ")
    header_b64, payload_b64, signature_b64 = token.split(".")
    # Flip the last character of the payload segment — any bit change there
    # invalidates the signature check without needing to forge a new one.
    flipped_char = "A" if payload_b64[-1] != "A" else "B"
    tampered = f"{header_b64}.{payload_b64[:-1]}{flipped_char}.{signature_b64}"

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tampered}"})
    assert response.status_code == 401


# --- injection-style input is inert, never executed or misinterpreted ---


def test_html_and_script_payloads_in_profile_fields_round_trip_as_literal_text(client):
    headers = _register_and_login(client)
    payload = "<script>alert('xss')</script>"
    response = client.put("/api/v1/profile", headers=headers, json={"bio": payload})
    assert response.status_code == 200
    # Stored and returned byte-for-byte as data, never templated into HTML
    # server-side — React escapes it on render, so this is a data-integrity
    # check, not a sanitization one.
    assert response.json()["data"]["bio"] == payload


def test_sql_injection_style_skill_name_is_stored_and_queried_safely(client):
    headers = _register_and_login(client)
    payload = "Robert'); DROP TABLE skills;--"
    response = client.post(
        "/api/v1/profile/skills", headers=headers, json={"name": payload, "category": "technical"}
    )
    assert response.status_code == 201
    assert response.json()["data"]["skill"]["name"] == payload

    # The skills table (and the rest of the schema) must still be intact —
    # every query in this app goes through the ORM's parameter binding, so a
    # string like this is never interpolated into SQL.
    listing = client.get("/api/v1/profile", headers=headers)
    assert listing.status_code == 200
    assert any(skill["skill"]["name"] == payload for skill in listing.json()["data"]["skills"])
