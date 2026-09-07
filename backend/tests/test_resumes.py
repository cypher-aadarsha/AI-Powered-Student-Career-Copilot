"""Coverage for Phase 5: resume upload, text extraction (PDF/DOCX), the
rule-based structured-data extraction (contact info, catalogue skill
matching), the heuristic AI analyzer, and cross-user ownership checks.

Uploaded files are written to `Settings.resume_storage_dir` — the
`_isolated_resume_storage` fixture below points that at a pytest tmp_path
for every test in this module so runs never touch the real backend/storage/
directory and never leak files between test runs.
"""
import io
import time
import uuid

import pytest
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.ai.extraction import detect_skills, extract_contact_info
from app.ai.provider import MockAIProvider
from app.core.config import get_settings
from app.models.resume import Resume

STUDENT_A = {"email": "asha@example.edu.np", "password": "password123", "full_name": "Asha Sharma"}
STUDENT_B = {"email": "bikash@example.edu.np", "password": "password123", "full_name": "Bikash Sainju"}

RESUME_LINES = [
    "Asha Sharma",
    "asha@example.edu.np | +977-9800000000",
    "https://github.com/asha | https://linkedin.com/in/asha",
    "",
    "Education",
    "BSc. CSIT, St. Xavier's College, expected 2027",
    "",
    "Experience",
    "Backend Intern, Some Company, 2025",
    "Built and led development of a Python REST API; improved response time by 30 percent.",
    "Automated the deployment pipeline and reduced release time significantly.",
    "",
    "Projects",
    "Career Copilot: built a resume parser and analyzer using Python and FastAPI, deployed on a VPS.",
    "",
    "Skills",
    "Python, FastAPI, PostgreSQL",
]


@pytest.fixture(autouse=True)
def _isolated_resume_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUME_STORAGE_DIR", str(tmp_path / "resumes"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _auth_headers(client, user=STUDENT_A) -> dict:
    client.post("/api/v1/auth/register", json=user)
    login = client.post("/api/v1/auth/login", json={"email": user["email"], "password": user["password"]})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_catalogue_skill(client, headers, name: str, category: str = "programming_language") -> None:
    response = client.post("/api/v1/profile/skills", headers=headers, json={"name": name, "category": category})
    assert response.status_code == 201


def _pdf_bytes(lines: list[str]) -> bytes:
    buffer = io.BytesIO()
    doc = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    for line in lines:
        doc.drawString(72, y, line)
        y -= 16
    doc.save()
    return buffer.getvalue()


def _docx_bytes(lines: list[str]) -> bytes:
    buffer = io.BytesIO()
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    document.save(buffer)
    return buffer.getvalue()


# --- upload + parsing + AI analysis --------------------------------------


def test_upload_pdf_resume_is_parsed_and_analyzed(client):
    headers = _auth_headers(client)
    _add_catalogue_skill(client, headers, "Python")

    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("resume.pdf", _pdf_bytes(RESUME_LINES), "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["status"] == "parsed"
    assert body["original_filename"] == "resume.pdf"
    assert "Python" in body["parsed_data"]["detected_skills"]
    assert body["parsed_data"]["github_url"] == "https://github.com/asha"
    assert body["parsed_data"]["emails"] == ["asha@example.edu.np"]
    assert 0 <= body["ai_score"] <= 100
    assert body["ai_summary"]
    assert isinstance(body["ai_strengths"], list)
    assert isinstance(body["ai_suggestions"], list)
    assert body["ai_provider_used"] == "mock"


def test_upload_docx_resume_is_parsed(client):
    headers = _auth_headers(client)
    _add_catalogue_skill(client, headers, "FastAPI", category="framework")

    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={
            "file": (
                "resume.docx",
                _docx_bytes(RESUME_LINES),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["status"] == "parsed"
    assert "FastAPI" in body["parsed_data"]["detected_skills"]


def test_upload_rejects_unsupported_file_type(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/resumes", headers=headers, files={"file": ("resume.txt", b"hello world", "text/plain")}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsupported_file_type"


def test_upload_rejects_oversized_file(client, monkeypatch):
    monkeypatch.setenv("RESUME_MAX_SIZE_MB", "1")
    get_settings.cache_clear()
    headers = _auth_headers(client)
    oversized = b"%PDF-1.4\n" + b"0" * (2 * 1024 * 1024)
    response = client.post(
        "/api/v1/resumes", headers=headers, files={"file": ("resume.pdf", oversized, "application/pdf")}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "file_too_large"
    get_settings.cache_clear()


def test_upload_of_corrupt_pdf_marks_resume_failed_instead_of_500(client):
    headers = _auth_headers(client)
    # Real PDF header, garbage body — passes the file-signature check at
    # upload time but still isn't a parseable PDF, so this exercises the
    # parser's own failure handling rather than upload validation.
    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("resume.pdf", b"%PDF-1.4\nthis is not a valid pdf body", "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["status"] == "failed"
    assert body["parse_error"]


def test_upload_rejects_a_file_whose_content_does_not_match_its_declared_type(client):
    # Content-Type is a client-supplied header — an attacker can label any
    # bytes "application/pdf". The file's actual signature (magic bytes) is
    # checked too, so a mismatched upload is rejected before it reaches the
    # parser, not silently trusted.
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("resume.pdf", b"hello world, not actually a pdf", "application/pdf")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsupported_file_type"


def test_upload_without_auth_returns_401(client):
    response = client.post(
        "/api/v1/resumes", files={"file": ("resume.pdf", _pdf_bytes(RESUME_LINES), "application/pdf")}
    )
    assert response.status_code == 401


def test_upload_with_a_path_traversal_filename_is_stored_safely(client, db_session):
    # The client-supplied filename is never used to build the on-disk path
    # beyond its extension — the file itself is always written under a
    # server-generated uuid — so a malicious filename can't escape the
    # per-profile storage directory.
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("../../../etc/passwd.pdf", _pdf_bytes(["hi"]), "application/pdf")},
    )
    assert response.status_code == 201
    resume_id = uuid.UUID(response.json()["data"]["id"])
    resume = db_session.get(Resume, resume_id)
    assert ".." not in resume.storage_path
    assert resume.storage_path.endswith(".pdf")


# --- list / get / delete / reanalyze, ownership scoping -------------------


def test_list_resumes_returns_all_uploads_newest_first(client):
    # SQLite's CURRENT_TIMESTAMP (what `func.now()` compiles to on this dialect)
    # only has 1-second resolution, unlike Postgres — force the two uploads
    # into different seconds so "newest first" is unambiguous to assert.
    headers = _auth_headers(client)
    client.post("/api/v1/resumes", headers=headers, files={"file": ("a.pdf", _pdf_bytes(["A"]), "application/pdf")})
    time.sleep(1.1)
    client.post("/api/v1/resumes", headers=headers, files={"file": ("b.pdf", _pdf_bytes(["B"]), "application/pdf")})

    response = client.get("/api/v1/resumes", headers=headers)
    assert response.status_code == 200
    filenames = [r["original_filename"] for r in response.json()["data"]]
    assert filenames == ["b.pdf", "a.pdf"]


def test_get_and_delete_resume_are_scoped_to_owner(client):
    headers_a = _auth_headers(client, STUDENT_A)
    upload = client.post(
        "/api/v1/resumes", headers=headers_a, files={"file": ("resume.pdf", _pdf_bytes(RESUME_LINES), "application/pdf")}
    )
    resume_id = upload.json()["data"]["id"]

    headers_b = _auth_headers(client, STUDENT_B)
    assert client.get(f"/api/v1/resumes/{resume_id}", headers=headers_b).status_code == 404
    assert client.delete(f"/api/v1/resumes/{resume_id}", headers=headers_b).status_code == 404

    assert client.get(f"/api/v1/resumes/{resume_id}", headers=headers_a).status_code == 200
    assert client.delete(f"/api/v1/resumes/{resume_id}", headers=headers_a).status_code == 204
    assert client.get(f"/api/v1/resumes/{resume_id}", headers=headers_a).status_code == 404


def test_reanalyze_recomputes_ai_fields(client):
    headers = _auth_headers(client)
    upload = client.post(
        "/api/v1/resumes", headers=headers, files={"file": ("resume.pdf", _pdf_bytes(RESUME_LINES), "application/pdf")}
    )
    resume_id = upload.json()["data"]["id"]

    response = client.post(f"/api/v1/resumes/{resume_id}/reanalyze", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["ai_provider_used"] == "mock"


def test_reanalyze_unparsed_resume_returns_409(client):
    headers = _auth_headers(client)
    upload = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("resume.pdf", b"%PDF-1.4\nnot a real pdf body", "application/pdf")},
    )
    resume_id = upload.json()["data"]["id"]
    response = client.post(f"/api/v1/resumes/{resume_id}/reanalyze", headers=headers)
    assert response.status_code == 409


# --- AI/extraction unit tests (no HTTP/DB needed) -------------------------


def test_extract_contact_info_finds_email_and_links():
    text = "Reach me at asha@example.edu.np or https://github.com/asha and https://linkedin.com/in/asha"
    info = extract_contact_info(text)
    assert info["emails"] == ["asha@example.edu.np"]
    assert info["github_url"] == "https://github.com/asha"
    assert info["linkedin_url"] == "https://linkedin.com/in/asha"


def test_detect_skills_matches_whole_words_only():
    assert detect_skills("I know C++ and Java well", ["C++", "Java", "JavaScript"]) == ["C++", "Java"]


def test_mock_ai_provider_rewards_detected_content():
    rich_analysis = MockAIProvider().analyze_resume(
        text=" ".join(RESUME_LINES * 6), detected_skills=["Python", "FastAPI", "PostgreSQL"]
    )
    empty_analysis = MockAIProvider().analyze_resume(text="", detected_skills=[])
    assert rich_analysis.score > empty_analysis.score
    assert rich_analysis.provider_used == "mock"
    assert empty_analysis.suggestions
