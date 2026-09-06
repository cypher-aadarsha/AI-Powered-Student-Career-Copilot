"""Coverage for Phase 8: mock interview sessions (question selection,
role-aware technical questions, one-answer-per-question, auto-completion),
the heuristic feedback provider, and cross-user ownership checks.
"""
import pytest

from app.ai.interview_provider import MockInterviewFeedbackProvider
from seed.career_roles import seed_career_roles
from seed.interview_questions import QUESTIONS, seed_interview_questions

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}
STUDENT_B = {"email": "bikash@example.edu.np", "password": "password123", "full_name": "Bikash Sainju"}

DETAILED_ANSWER = (
    "In the situation, our team faced a tight deadline and conflicting priorities. My task was to "
    "coordinate the backend work. I took the action of splitting the work into smaller chunks and "
    "checking in daily, which reduced our bug count by 30 percent. The result was we shipped on time "
    "with a stable release."
)


@pytest.fixture(autouse=True)
def _seed_catalogue(db_session):
    seed_career_roles(db_session)
    seed_interview_questions(db_session)


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _start_session(client, headers, **kwargs) -> dict:
    response = client.post("/api/v1/interviews/sessions", headers=headers, json=kwargs)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def _find_role_id(client, headers, title: str) -> str:
    response = client.get("/api/v1/careers", headers=headers)
    match = next(item for item in response.json()["data"] if item["role"]["title"] == title)
    return match["role"]["id"]


# --- session creation --------------------------------------------------


def test_start_session_without_auth_returns_401(client):
    response = client.post("/api/v1/interviews/sessions", json={})
    assert response.status_code == 401


def test_start_session_default_mixes_categories(client):
    headers = _auth_headers(client)
    session = _start_session(client, headers)
    assert len(session["questions"]) == 5
    categories = {q["category"] for q in session["questions"]}
    assert "technical" in categories
    assert categories & {"behavioral", "situational"}
    assert session["status"] == "in_progress"
    assert session["career_role"] is None


def test_start_session_with_unknown_role_returns_404(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/interviews/sessions",
        headers=headers,
        json={"career_role_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404


def test_start_session_with_role_prefers_role_specific_technical_questions(client):
    headers = _auth_headers(client)
    role_id = _find_role_id(client, headers, "Backend Developer")
    session = _start_session(client, headers, career_role_id=role_id, question_count=9)

    backend_skills = {"Python", "SQL", "REST APIs", "Git", "Docker", "PostgreSQL", "FastAPI"}
    technical_questions = [q for q in session["questions"] if q["category"] == "technical"]
    assert technical_questions  # at least some technical questions were assigned
    for question in technical_questions:
        skill_names = {s["name"] for s in question["skills"]}
        assert skill_names & backend_skills, f"{question['question_text']!r} isn't tagged to a backend skill"


def test_start_session_question_count_is_bounded(client):
    headers = _auth_headers(client)
    assert client.post("/api/v1/interviews/sessions", headers=headers, json={"question_count": 2}).status_code == 422
    assert client.post("/api/v1/interviews/sessions", headers=headers, json={"question_count": 11}).status_code == 422


# --- answers -------------------------------------------------------------


def test_submit_answer_returns_feedback_and_score(client):
    headers = _auth_headers(client)
    session = _start_session(client, headers)
    question_id = session["questions"][0]["id"]

    response = client.post(
        f"/api/v1/interviews/sessions/{session['id']}/answers",
        headers=headers,
        json={"question_id": question_id, "answer_text": DETAILED_ANSWER},
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert 0 <= body["ai_score"] <= 100
    assert body["ai_feedback"]
    assert body["ai_provider_used"] == "mock"


def test_submit_answer_for_question_not_in_session_returns_404(client):
    headers = _auth_headers(client)
    session_a = _start_session(client, headers, question_count=3)
    session_b = _start_session(client, headers, question_count=3)
    foreign_question_id = next(
        q["id"] for q in session_b["questions"] if q["id"] not in {q2["id"] for q2 in session_a["questions"]}
    )

    response = client.post(
        f"/api/v1/interviews/sessions/{session_a['id']}/answers",
        headers=headers,
        json={"question_id": foreign_question_id, "answer_text": DETAILED_ANSWER},
    )
    assert response.status_code == 404


def test_submit_answer_twice_returns_409(client):
    headers = _auth_headers(client)
    session = _start_session(client, headers)
    question_id = session["questions"][0]["id"]
    payload = {"question_id": question_id, "answer_text": DETAILED_ANSWER}

    assert client.post(f"/api/v1/interviews/sessions/{session['id']}/answers", headers=headers, json=payload).status_code == 201
    response = client.post(f"/api/v1/interviews/sessions/{session['id']}/answers", headers=headers, json=payload)
    assert response.status_code == 409


def test_session_auto_completes_once_every_question_is_answered(client):
    headers = _auth_headers(client)
    session = _start_session(client, headers, question_count=3)

    for question in session["questions"]:
        client.post(
            f"/api/v1/interviews/sessions/{session['id']}/answers",
            headers=headers,
            json={"question_id": question["id"], "answer_text": DETAILED_ANSWER},
        )

    response = client.get(f"/api/v1/interviews/sessions/{session['id']}", headers=headers)
    body = response.json()["data"]
    assert body["status"] == "completed"
    assert body["completed_at"] is not None
    assert body["average_score"] is not None


# --- listing, ownership ----------------------------------------------------


def test_list_sessions_shows_progress_and_average(client):
    headers = _auth_headers(client)
    session = _start_session(client, headers, question_count=3)
    client.post(
        f"/api/v1/interviews/sessions/{session['id']}/answers",
        headers=headers,
        json={"question_id": session["questions"][0]["id"], "answer_text": DETAILED_ANSWER},
    )

    response = client.get("/api/v1/interviews/sessions", headers=headers)
    assert response.status_code == 200
    item = next(s for s in response.json()["data"] if s["id"] == session["id"])
    assert item["question_count"] == 3
    assert item["answered_count"] == 1
    assert item["status"] == "in_progress"
    assert item["average_score"] is not None


def test_get_session_and_answers_are_scoped_to_owner(client):
    headers_a = _auth_headers(client, STUDENT_A)
    session = _start_session(client, headers_a, question_count=3)

    headers_b = _auth_headers(client, STUDENT_B)
    assert client.get(f"/api/v1/interviews/sessions/{session['id']}", headers=headers_b).status_code == 404
    response = client.post(
        f"/api/v1/interviews/sessions/{session['id']}/answers",
        headers=headers_b,
        json={"question_id": session["questions"][0]["id"], "answer_text": DETAILED_ANSWER},
    )
    assert response.status_code == 404


def test_get_session_for_unknown_id_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/interviews/sessions/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


def test_seed_interview_questions_is_idempotent(db_session):
    first_run = seed_interview_questions(db_session)
    second_run = seed_interview_questions(db_session)
    assert first_run == 0  # already seeded by the autouse fixture
    assert second_run == 0
    assert len(QUESTIONS) > 0


# --- heuristic feedback provider unit tests (no HTTP/DB needed) -----------


def test_short_answer_gets_length_feedback():
    result = MockInterviewFeedbackProvider().evaluate_answer(
        question_text="Tell me about yourself.", model_answer=None, answer_text="I like coding."
    )
    assert any("short" in item.lower() for item in result.feedback)


def test_star_structured_answer_scores_higher_than_unstructured():
    provider = MockInterviewFeedbackProvider()
    structured = provider.evaluate_answer(
        question_text="Tell me about a challenge.", model_answer=None, answer_text=DETAILED_ANSWER
    )
    unstructured = provider.evaluate_answer(
        question_text="Tell me about a challenge.",
        model_answer=None,
        answer_text="It was fine, we finished the project eventually after some back and forth discussions.",
    )
    assert structured.score > unstructured.score


def test_answer_matching_model_answer_keywords_scores_higher():
    provider = MockInterviewFeedbackProvider()
    model_answer = (
        "Lists are mutable and typically used for collections that change; tuples are immutable and "
        "often used for fixed collections or as dictionary keys."
    )
    on_topic = provider.evaluate_answer(
        question_text="List vs tuple?",
        model_answer=model_answer,
        answer_text="Lists are mutable collections that change, while tuples are immutable and often used as dictionary keys.",
    )
    off_topic = provider.evaluate_answer(
        question_text="List vs tuple?",
        model_answer=model_answer,
        answer_text="I would open my code editor and start writing some functions to solve the problem at hand.",
    )
    assert on_topic.score > off_topic.score
