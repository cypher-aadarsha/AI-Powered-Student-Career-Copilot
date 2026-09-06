"""Coverage for Phase 7's job-matching module: ranked list, per-job detail,
and reuse of the same skill_gap engine the career module uses (all of a
job's skills are treated as "required", no preferred split).
"""
import pytest

from seed.job_postings import JOBS, seed_job_postings

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}
STUDENT_B = {"email": "bikash@example.edu.np", "password": "password123", "full_name": "Bikash Sainju"}


@pytest.fixture(autouse=True)
def _seed_jobs(db_session):
    seed_job_postings(db_session)


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_skill(client, headers, name: str, proficiency: str = "expert") -> None:
    response = client.post(
        "/api/v1/profile/skills",
        headers=headers,
        json={"name": name, "category": "technical", "proficiency_level": proficiency},
    )
    assert response.status_code == 201


def _find_job_id(client, headers, title: str) -> str:
    response = client.get("/api/v1/jobs", headers=headers)
    match = next(item for item in response.json()["data"] if item["job"]["title"] == title)
    return match["job"]["id"]


def test_list_jobs_without_auth_returns_401(client):
    assert client.get("/api/v1/jobs").status_code == 401


def test_list_jobs_returns_every_seeded_posting(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/jobs", headers=headers)
    assert response.status_code == 200
    titles = {item["job"]["title"] for item in response.json()["data"]}
    assert titles == {job[0] for job in JOBS}


def test_student_with_no_skills_scores_zero_on_every_job(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/jobs", headers=headers)
    assert all(item["score"] == 0 for item in response.json()["data"])


def test_matching_job_ranks_first_and_scores_100(client):
    headers = _auth_headers(client)
    for skill in ("Python", "SQL", "Git"):
        _add_skill(client, headers, skill)

    response = client.get("/api/v1/jobs", headers=headers)
    ranked = response.json()["data"]
    assert ranked[0]["job"]["title"] == "Backend Developer Intern"
    assert ranked[0]["score"] == 100
    scores = [item["score"] for item in ranked]
    assert scores == sorted(scores, reverse=True)


def test_job_detail_lists_matched_and_missing_skills(client):
    headers = _auth_headers(client)
    _add_skill(client, headers, "Python")
    job_id = _find_job_id(client, headers, "Backend Developer Intern")

    response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["job"]["company"] == "Nimbus Cloud Labs"
    assert body["apply_url"].startswith("https://example.com/")
    matched_names = {m["skill"]["name"] for m in body["matched_skills"]}
    assert matched_names == {"Python"}
    missing_names = {s["name"] for s in body["missing_skills"]}
    assert missing_names == {"SQL", "Git"}


def test_job_detail_for_unknown_id_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


def test_job_scores_are_isolated_per_student(client):
    headers_a = _auth_headers(client, STUDENT_A)
    for skill in ("Python", "SQL", "Git"):
        _add_skill(client, headers_a, skill)

    headers_b = _auth_headers(client, STUDENT_B)
    job_id = _find_job_id(client, headers_b, "Backend Developer Intern")
    response = client.get(f"/api/v1/jobs/{job_id}", headers=headers_b)
    assert response.json()["data"]["score"] == 0


def test_seed_job_postings_is_idempotent(db_session):
    first_run = seed_job_postings(db_session)
    second_run = seed_job_postings(db_session)
    assert first_run == 0  # already seeded by the autouse fixture
    assert second_run == 0
