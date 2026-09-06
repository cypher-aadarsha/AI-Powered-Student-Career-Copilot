# Career Copilot — Backend

FastAPI + SQLAlchemy + PostgreSQL. See the repo root `README.md` for how to run the full stack
via Docker Compose.

## Standalone commands

```bash
python -m venv .venv && .venv/Scripts/activate   # source .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head              # creates the schema against DATABASE_URL
python -m seed.career_roles       # one-time: populates the career-role catalogue (Phase 6)
uvicorn app.main:app --reload     # http://localhost:8000 — docs at /docs
pytest -v
```

To add a new migration after changing a model: `alembic revision --autogenerate -m "..."`, then
read the generated file before running it — autogenerate is a starting point, not ground truth.

## Structure

```
app/
  core/          Settings, logging, security (hashing/JWT), exception → HTTP mapping
  api/           deps.py (auth/RBAC guards) + v1/ routers — thin, delegate to services/
  db/            Engine/session + declarative base
  models/        SQLAlchemy models: user.py (Phase 3); student_profile.py, skill.py,
                 student_skill.py, project.py, experience.py, certification.py (Phase 4);
                 resume.py (Phase 5); career_role.py (Phase 6)
  schemas/       Pydantic request/response models
  services/      Business logic — routers never hash a password or query the DB directly.
                 skill_gap.py (Phase 6) is a pure, DB-free scoring function, deliberately kept
                 separate from career_service.py (which loads the data it scores)
  repositories/  Query objects — the only layer that writes SQLAlchemy queries
  ai/            Resume text extraction (parsing.py), structured-data extraction
                 (extraction.py), and the AIProvider interface + implementations
                 (provider.py) — Phase 5
migrations/      Alembic — 0001 (users), 0002 (profile/skills/projects/experiences/certifications),
                 0003 (resumes), 0004 (career roles)
seed/            career_roles.py (Phase 6) — the only seed loader so far; see below
tests/           pytest — conftest.py's `client` fixture runs against a disposable in-memory
                 SQLite DB (models use dialect-generic types for exactly this reason), so the
                 suite needs no live Postgres
```

## Career model (Phase 6)

- `career_roles` + `career_role_skills` are a **platform-curated catalogue**, not
  student-authored — there's no `POST /careers`. They're populated by `seed/career_roles.py`
  (`python -m seed.career_roles`, idempotent by title), and full admin CRUD for them is
  Phase 10's job.
- The skill-gap score (`app/services/skill_gap.py`) is a deterministic weighted formula, the
  same explainability philosophy as the resume analyzer's `MockAIProvider`: every required
  skill counts double a preferred one, and a matched skill earns partial credit from the
  student's proficiency level (beginner=0.5× … advanced/expert=1.0×) rather than a flat
  yes/no. `compute_skill_gap()` is a pure function over plain data — no DB, no HTTP — so it's
  unit-tested directly in `tests/test_careers.py` alongside the route-level tests.
- Nothing is stored per-student: `GET /careers` and `GET /careers/{id}` recompute the score
  fresh from the student's current `StudentSkill` rows on every request, so editing your
  profile skills immediately changes your career matches with no cache to invalidate.
- `GET /careers` doubles as the "recommendations" list — it returns every role already ranked
  by score, since the catalogue is small enough (~8 seeded roles) that a separate
  `/recommendations` endpoint would just be a truncated version of the same list.

## Resume model (Phase 5)

- `resumes` is one-to-many with `student_profiles` — re-uploading keeps history instead of
  overwriting; callers that want "the current one" take the most recent row (no separate
  `is_active` flag to keep in sync).
- Upload → parse → analyze all run **synchronously** inside `POST /resumes`, since this stack
  has no background job queue yet. A large file adds a few hundred ms to the response — an
  accepted trade-off at this scale, not a gap; a queue-based version would move parsing/analysis
  to a worker and let the client poll `status`.
- Parsing (`app/ai/parsing.py`) supports PDF (pdfplumber) and DOCX (python-docx) only; anything
  else is rejected with `422 unsupported_file_type` before it's ever written to disk. A corrupt
  or password-protected file that fails to parse marks the resume `failed` with a `parse_error`
  message rather than 500ing the request.
- Structured extraction (`app/ai/extraction.py`) is rule-based, not ML: regex for emails/
  phones/links, and a word-boundary match of each *existing catalogue skill name* against the
  resume text. It only ever confirms skills already in the shared catalogue (see Phase 4) — it
  doesn't invent new ones. Semantic/fuzzy matching is Phase 6's job.
- AI analysis (`app/ai/provider.py`) is behind an `AIProvider` interface: `MockAIProvider` (the
  default — deterministic, explainable, no network) scores against concrete rubric-driven
  checks (section presence, action verbs, quantified achievements, contact info, detected-skill
  count), with every point tied to a visible strength or suggestion. `LLMAIProvider` calls an
  OpenAI-chat-completions-compatible endpoint when `AI_PROVIDER=llm` and an API key/base URL are
  configured, and transparently falls back to the heuristic provider on any network or parsing
  failure — an upload should never fail just because the LLM is unreachable.
- Files live under `RESUME_STORAGE_DIR` (default `storage/resumes/<profile_id>/<uuid>.<ext>`,
  gitignored) — swapping to S3/object storage later only touches `ResumeService._save_file`.

## Profile model (Phase 4)

- `student_profiles` is one-to-one with `users`, created lazily on first `GET`/`PUT /profile`
  (not at registration) — auth and profile stay decoupled modules.
- `skills` is a shared catalogue, not per-student free text: adding a skill via
  `POST /profile/skills` resolves an existing catalogue row by case-insensitive name match
  before creating a new one, so "React" and "react" never become two rows.
- `projects` can tag the skills they used (`project_skills`); `PUT /profile/projects/{id}`
  replaces the tag set rather than diffing it — simple and correct at this scale.
- Every mutation on a sub-resource (skill/project/experience/certification) is scoped to the
  authenticated user's own profile; a request naming another student's resource id gets a 404,
  never a 403 — see `services/profile_service.py`'s module docstring for why.

## Auth model (Phase 3)

- Passwords: bcrypt via passlib (`core/security.py`).
- Sessions: stateless JWT bearer tokens (`Authorization: Bearer <token>`), 60 min expiry by
  default. `POST /auth/logout` exists for a consistent client-side call site but doesn't
  invalidate anything server-side yet — see the Technical Design Document's risk register for
  the accepted trade-off.
- Roles: `student` (default, the only self-registerable role) and `admin` (provisioned
  out-of-band — never chosen by the registering user). `api/deps.py`'s `require_role(...)`
  guards any admin-only route; `GET /api/v1/admin/ping` is a placeholder proving the guard until
  Phase 10 builds the real admin CRUD surfaces.
