# Career Copilot — Backend

FastAPI + SQLAlchemy + PostgreSQL. See the repo root `README.md` for how to run the full stack
via Docker Compose.

## Standalone commands

```bash
python -m venv .venv && .venv/Scripts/activate   # source .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head                    # creates the schema against DATABASE_URL
python -m seed.career_roles             # one-time: career-role catalogue (Phase 6)
python -m seed.learning_resources       # one-time: learning-resource catalogue (Phase 7)
python -m seed.job_postings             # one-time: demo job postings (Phase 7)
python -m seed.interview_questions      # one-time: interview question bank (Phase 8)
ADMIN_PASSWORD=... python -m seed.create_admin  # one-time: your admin login (Phase 10)
uvicorn app.main:app --reload           # http://localhost:8000 — docs at /docs
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
                 resume.py (Phase 5); career_role.py (Phase 6); learning_resource.py,
                 job_posting.py (Phase 7); interview_question.py, mock_interview.py (Phase 8).
                 No new tables in Phase 9 or 10 — the dashboard is read-only composition and
                 the admin panel manages rows in tables that already existed.
  schemas/       Pydantic request/response models. skill_match.py's MatchedSkill is shared
                 between career.py and job.py — both run their skills through the same
                 skill_gap engine and return the same "skill + proficiency" shape.
                 dashboard.py reuses CareerListItem/JobListItem as-is for the "top matches"
                 cards rather than defining a second shape for the same data. admin.py
                 (Phase 10) takes skills by name (AdminSkillRef), not id, on every write
                 request — see its docstring for why
  services/      Business logic — routers never hash a password or query the DB directly.
                 skill_gap.py (Phase 6) is a pure, DB-free scoring function, deliberately kept
                 separate from career_service.py/job_service.py (which load the data it scores).
                 learning_service.py (Phase 7) composes CareerService rather than recomputing
                 gaps itself — "what's missing" is Phase 6's job, "how do I learn it" is Phase 7's.
                 interview_service.py (Phase 8) picks a session's fixed question set once at
                 start time and scores each answer through app/ai/interview_provider.py.
                 dashboard_service.py (Phase 9) composes ProfileRepository/CareerService/
                 JobService/MockInterviewSessionRepository — it computes nothing those modules
                 don't already compute, except profile-completion scoring and suggested actions.
                 admin_service.py (Phase 10) composes all four catalogue repositories plus
                 UserRepository — one service for the whole admin surface, the same shape as
                 LearningService composing CareerService
  repositories/  Query objects — the only layer that writes SQLAlchemy queries. Every
                 repository that was read-only through Phase 9 (career_role, learning_resource,
                 job_posting, interview_question) gained create/update/delete/set_skills methods
                 in Phase 10 — admin_service.py is their only caller
  ai/            Resume text extraction (parsing.py), structured-data extraction
                 (extraction.py), and the AIProvider interface + implementations
                 (provider.py) — Phase 5. interview_provider.py (Phase 8) is the same
                 heuristic-default/LLM-if-configured pattern applied to interview-answer
                 feedback instead of resume text — see its docstring for why it's a separate
                 module rather than reusing AIProvider's method signature
migrations/      Alembic — 0001 (users), 0002 (profile/skills/projects/experiences/certifications),
                 0003 (resumes), 0004 (career roles), 0005 (learning resources + job postings),
                 0006 (interview questions + mock interview sessions/answers). Nothing added
                 in Phase 9 or 10 — no new tables either phase.
seed/            career_roles.py (Phase 6), learning_resources.py + job_postings.py (Phase 7),
                 interview_questions.py (Phase 8), create_admin.py (Phase 10, the only one that
                 isn't a catalogue — provisions the first admin login) — all idempotent
                 (catalogues by title, job postings by title+company, the admin script by
                 email); see below
tests/           pytest — conftest.py's `client` fixture runs against a disposable in-memory
                 SQLite DB (models use dialect-generic types for exactly this reason), so the
                 suite needs no live Postgres. Since Phase 10, that DB also runs with SQLite's
                 FOREIGN KEY enforcement turned on (off by default, unlike Postgres) — see
                 conftest.py's `_enable_sqlite_foreign_keys` and the admin module notes below
```

## Admin panel (Phase 10)

- Every route under `/admin` is guarded once, at the router level
  (`app/api/v1/admin/__init__.py`'s `dependencies=[Depends(require_role(UserRole.admin))]`) —
  individual sub-routers (`users.py`, `career_roles.py`, `learning_resources.py`,
  `job_postings.py`, `interview_questions.py`) never repeat the guard. This is the
  `admin.py` placeholder from Phase 3 turning into the package its own docstring predicted
  it eventually would.
- **Admin accounts are never created by self-registration** (`AuthService.register` always
  creates a `student`) — the only way in is `seed/create_admin.py`
  (`ADMIN_PASSWORD=... python -m seed.create_admin`), idempotent by email, reading the
  password from an environment variable so it never lives in source control. Its default
  email is deliberately a real-looking domain (`careercopilot.io`), not `.local`/`.test`/
  `.example` — those are IANA special-use TLDs that `EmailStr` (the same schema `/auth/login`
  validates against) rejects outright, which would silently create an admin account nobody
  could actually log into. `tests/test_admin.py` has a regression test for exactly this.
- **User moderation** is `GET /admin/users` + `PATCH /admin/users/{id}` (`{"is_active": bool}`).
  Deactivating blocks login immediately (`AuthService.authenticate` already checked
  `is_active`, from Phase 3) without touching any of that user's data. An admin can't
  deactivate their own account (`400 cannot_deactivate_self`) — a guardrail against locking
  yourself out with no other admin to undo it.
- **Catalogue CRUD**: `career-roles`, `learning-resources`, `job-postings`, and
  `interview-questions` each get `GET` (list), `POST`, `PUT /{id}`, `DELETE /{id}`. Every
  write request gives skills by **name + category** (`AdminSkillRef`), the same shape the
  student-facing "add skill" form already uses, resolved via `SkillRepository.get_or_create`
  — an admin can introduce a brand-new skill while creating a role/job/resource/question in
  one step, instead of needing a separate "manage skills" screen first.
- `career_roles.title` has a real DB unique constraint, so creating/renaming to a duplicate
  title is caught and returned as `409 conflict` rather than a raw `IntegrityError`.
- Deleting an `interview_question` is the one delete in this app that can legitimately
  conflict: `mock_interview_session_questions`/`mock_interview_answers` reference it with
  `ondelete="RESTRICT"` once a student has actually used it in a session. `AdminService.
  delete_interview_question` flushes immediately (rather than leaving it to the route's later
  commit) specifically to catch that and translate it into a clean `409`, not a `500`. The
  other three catalogues have no such reference and can't hit this.
- `learning-resources` read responses reuse `LearningResourcePublic` from `schemas/learning.py`
  as-is — the shape an admin needs is identical to what students already see, so a second copy
  of the same schema would only drift out of sync over time.

## Dashboard module (Phase 9)

- `GET /dashboard` is the only new endpoint — a read-only aggregate of what every earlier
  phase's service already computes, gathered into one response so the frontend renders its
  home page in one round trip instead of six. No new tables.
- **Profile completion** (`compute_profile_completion` in `dashboard_service.py`) is an
  equally-weighted 9-item checklist (academic info, bio, 1+ skill, 3+ skills, 1+ project,
  experience, a certification, a resume, a social/portfolio link) — same "every point maps to
  one visible, explainable reason" philosophy as the resume analyzer and the skill-gap formula,
  just applied to profile completeness instead of a score. It's a pure function tested directly
  in `tests/test_dashboard.py`, independent of the DB.
- **Suggested actions** is a short rule-based list (resume missing → upload it; fewer than 3
  skills → add more; no projects → add one; no interview sessions → try one; best career match
  under 50% → check its gap), capped at 4 and evaluated in that priority order — the same
  "explainable, not a black box" stance as everything else the AI/scoring layer produces here.
- Everything else — latest resume, top 3 career matches, top 3 job matches, interview stats — is
  exactly what `ResumeRepository`/`CareerService`/`JobService`/`MockInterviewSessionRepository`
  already return; the dashboard route just slices and re-wraps it, so a change to how those
  modules score something is automatically reflected on the dashboard with no duplicated logic.

## Interview module (Phase 8)

- `interview_questions` + `interview_question_skills` are a **platform-curated bank**, same
  pattern as the other catalogues — seeded via `seed/interview_questions.py`. Behavioral and
  situational questions are typically untagged (general); technical questions are tagged with
  the skill they probe.
- `POST /interviews/sessions` picks a session's question set **once, at start time** — a mix of
  non-technical (behavioral/situational, at least 1) and technical questions, roughly a third
  non-technical by default. If `career_role_id` is given, technical questions are filtered to
  ones tagged with that role's skills first, falling back to the general technical pool only if
  none match. The assigned set is stored in `mock_interview_session_questions` (a join table,
  since the same shared question can appear in many sessions) so it stays fixed even if the
  question bank changes later.
- `POST /interviews/sessions/{id}/answers` is one-answer-per-question (`409 conflict` on a
  repeat) and `404`s if the question wasn't actually assigned to that session — same
  don't-leak-existence philosophy as the rest of the app. Submitting the last unanswered
  question auto-transitions the session to `completed` and stamps `completed_at`.
- Feedback (`app/ai/interview_provider.py`) mirrors the resume analyzer's design exactly:
  `MockInterviewFeedbackProvider` (default) scores answer length, whether it's backed by a
  concrete number, STAR-method structure (situation/task/action/result keywords), and — when
  the question has a `model_answer` — keyword overlap with it, as an explainable proxy for
  "did you cover the key ideas." `LLMInterviewFeedbackProvider` calls the same configured LLM
  endpoint as the resume/career modules and falls back to the heuristic on any failure.
- `average_score` is computed from `answers` at response time in `api/v1/interviews.py`, never
  stored — same reasoning as the career module's on-the-fly scoring.

## Learning & job modules (Phase 7)

- `learning_resources` + `learning_resource_skills` and `job_postings` + `job_posting_skills`
  are both **platform-curated catalogues**, same pattern as `career_roles` (Phase 6) — seeded via
  `seed/learning_resources.py` and `seed/job_postings.py`, no student-facing create endpoint.
  Every learning-resource URL points at a real, stable, top-level page from a well-known
  provider (official docs, freeCodeCamp, Khan Academy, etc.); every job posting is clearly
  fictional demo data with an `apply_url` on `example.com` (RFC 2606's reserved domain) so it's
  never mistaken for a real listing.
- `GET /learning-resources?skill_id=` lists resources, optionally filtered to ones teaching a
  given skill; `GET /careers/{role_id}/learning-plan` (on the *careers* router, since it's
  career-scoped) reuses `CareerService.get_role_detail` to find what's missing, then attaches
  resources per missing skill — Phase 6 finds the gap, Phase 7 finds the fix.
- `GET /jobs` and `GET /jobs/{id}` mirror the career endpoints exactly, but a job's skill list
  has no required/preferred split — every skill is passed to `compute_skill_gap()` as
  "required" with an empty preferred list, reusing the exact same weighted-proficiency formula
  instead of inventing a second scoring rule for jobs.

## Career model (Phase 6)

- `career_roles` + `career_role_skills` are a **platform-curated catalogue**, not
  student-authored — there's no student-facing `POST /careers`. They're populated by
  `seed/career_roles.py` (`python -m seed.career_roles`, idempotent by title) and, since
  Phase 10, manageable directly by an admin at `/admin/career-roles` (see that section above).
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
  doesn't invent new ones. (Phase 6/7's skill-gap matching turned out to be a deterministic
  weighted formula too, not semantic embeddings — see `app/services/skill_gap.py`.)
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
  out-of-band via `seed/create_admin.py` — never chosen by the registering user). `api/deps.py`'s
  `require_role(...)` guards every route under `/admin` (see the Admin panel section above for
  the full Phase 10 surface); `GET /api/v1/admin/ping` remains as a minimal smoke test of the
  guard itself, separate from any real resource.
