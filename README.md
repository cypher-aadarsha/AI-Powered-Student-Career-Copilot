# AI-Powered Student Career Copilot

A career-readiness platform for university/college students: upload a resume, pick a target
career role, get an explainable skill-gap score, and work through a personalized learning,
job-matching, and interview-prep roadmap.

BSc. CSIT 6th Semester Software Engineering project — built as a production-quality, modular
monolith rather than a toy CRUD demo. The full architecture, database design, algorithms, and
phased delivery plan are documented in the **Technical Design Document** (Phase 1 deliverable).

**Status:** Phase 11 — Testing & Security Hardening. Auth endpoints are now rate-limited against
brute-force/credential-stuffing, every response carries defensive HTTP headers, resume uploads are
validated by actual file signature (not just the client-supplied Content-Type) and read with a
bounded stream instead of trusting an unbounded size, and the test suite grew adversarial coverage
(tampered/expired/forged JWTs, path-traversal filenames, injection-style input). The frontend
gained its first unit tests (Vitest + React Testing Library). Every other feature module lands in
the phases that follow.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, React Hook Form + Zod |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic migrations |
| AI/NLP | pdfplumber, python-docx (Phase 5); skill-gap matching (Phase 6/7) is a deterministic weighted formula, not embeddings — see backend/README |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| DevOps | Docker, Docker Compose, pytest, Vitest + React Testing Library (Phase 11) |

## Project structure

```
.
├── backend/          FastAPI app — see backend/README below for its internal layout
├── frontend/          Next.js app (App Router)
├── docker-compose.yml Wires frontend + backend + Postgres together
└── README.md          You are here
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Compose v2) — **or**, for
  running services individually without Docker: Node.js ≥ 20.9, Python ≥ 3.12, and a local
  PostgreSQL 16 instance.

## Running with Docker Compose (recommended)

```bash
# 1. Copy environment templates (already done in this repo's initial commit —
#    re-run only if you deleted the local copies or are cloning fresh):
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 2. Build and start everything:
docker compose up --build
```

The backend container runs `alembic upgrade head` on boot, so the database schema is always
current — no manual migration step needed under Docker.

The backend container does **not** seed the curated catalogues automatically (that's reference
data, not user data) — run these once after the containers are up:

```bash
docker compose exec backend python -m seed.career_roles
docker compose exec backend python -m seed.learning_resources
docker compose exec backend python -m seed.job_postings
docker compose exec backend python -m seed.interview_questions
```

Admin accounts are provisioned the same way — out-of-band, never through self-registration:

```bash
docker compose exec -e ADMIN_PASSWORD=change-me backend python -m seed.create_admin
```

Then open:
- **Frontend:** http://localhost:3000 — register an account, log in, and land on your dashboard
  at `/`. From there: fill in your profile at `/profile`, upload a resume for parsing + AI
  analysis at `/resume`, see your ranked career matches at `/careers`, browse `/learning`
  resources, check `/jobs` for skill-matched demo postings, and practice at `/interviews`. Log in
  with a seeded admin account to manage the catalogues and moderate users at `/admin`.
- **Backend API docs (OpenAPI/Swagger):** http://localhost:8000/docs
- **Health check:** http://localhost:8000/api/v1/health

Stop with `Ctrl+C`, then `docker compose down` (add `-v` to also drop the Postgres volume).

Changed `frontend/`'s code and only see the old behavior? `NEXT_PUBLIC_API_URL` and any other
`NEXT_PUBLIC_*` variable are baked into the client bundle at *build* time — rerun
`docker compose build frontend` (or `up --build`) rather than just restarting the container.

## Running without Docker

**Backend**
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # then point DATABASE_URL at your local Postgres
alembic upgrade head
python -m seed.career_roles        # one-time: career-role catalogue (Phase 6)
python -m seed.learning_resources  # one-time: learning-resource catalogue (Phase 7)
python -m seed.job_postings        # one-time: demo job postings (Phase 7)
python -m seed.interview_questions # one-time: interview question bank (Phase 8)
ADMIN_PASSWORD=change-me python -m seed.create_admin  # one-time: your admin login (Phase 10)
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Testing

```bash
# Backend — 125 tests: health, auth (hashing, registration, login, JWT-gated routes, RBAC),
# the profile module (core fields, skills with case-insensitive dedup, projects with skill
# tagging, experiences, certifications, cross-user ownership checks), the resume module
# (PDF/DOCX upload + parsing, contact-info/skill extraction, the heuristic AI analyzer,
# file-type/size/signature validation, path-traversal-safe storage, ownership scoping), the
# career module (skill-gap scoring formula, ranked recommendations, per-role detail,
# seed-script idempotency), the learning/job modules (resource browsing + skill filter, the
# role learning-plan endpoint, job-posting ranking reusing the same skill-gap engine), the
# interview module (role-aware question selection, one-answer-per-question, auto-completion,
# the heuristic feedback provider's scoring rules), the dashboard module (profile-completion
# scoring, latest resume, top matches, interview stats, the suggested-actions rules), the
# admin module (role-guard enforcement, CRUD over all four catalogues, user moderation
# including the can't-deactivate-yourself guard, and the delete-blocked-when-in-use conflict
# path — which is also why the test DB now runs with SQLite's FOREIGN KEY enforcement turned
# on, see tests/conftest.py), and Phase 11's security hardening (defensive response headers,
# auth rate limiting, tampered/expired/forged JWTs, path-traversal filenames, injection-style
# input). Runs against a disposable in-memory SQLite DB, no Postgres needed.
cd backend && pytest -v

# Frontend — build + lint + unit tests (Vitest + React Testing Library, Phase 11): Zod schema
# edge cases (auth, profile) and presentational components (InlineConfirmButton's two-step
# flow, ScoreBar's color thresholds, the admin SkillRefInput chip list). Full page flows are
# still verified by hand in a real browser each phase — see each README's design-decision
# sections for what was checked that way.
cd frontend && npm run build && npm run lint && npm run test
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example` — every variable the app reads is
documented there. Never commit `.env` / `.env.local`; only the `.env.example` templates are
version-controlled.

## Security (Phase 11)

- **Auth rate limiting**: `/auth/login` and `/auth/register` are capped per client IP (20
  requests/60s) to blunt brute-force and credential-stuffing loops. In-memory, single-process —
  see `backend/app/core/rate_limit.py`'s docstring for what a Redis-backed limiter would add
  under multiple workers.
- **Defensive HTTP headers** on every response (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`; `Strict-Transport-Security` only when
  `ENVIRONMENT=production`) — see `backend/app/core/security_headers.py`.
- **Resume upload hardening**: the file's actual signature (magic bytes) is checked, not just the
  client-supplied `Content-Type` header, and the upload is read in bounded chunks rather than
  buffering an attacker-supplied size into memory before checking it.
- **Dependency audit**: `pip-audit` initially flagged 24 known vulnerabilities across 6 backend
  packages; `npm audit` reported 0 for the frontend. Every fixable backend finding was bumped
  (`fastapi`, `starlette`, `python-jose`, `python-multipart`, `pdfplumber`→`pdfminer.six` — see
  `backend/requirements.txt`'s inline comments for exactly which CVEs each bump addresses),
  bringing it down to 3 remaining findings, none of them reachable in this app: `ecdsa` and
  `pyasn1` (both pulled in transitively by `python-jose` for RSA/EC key handling, with no fix
  version available that respects `python-jose`'s own pin) are only ever exercised by JWT
  algorithms this app never uses — every token here is signed with HS256 — and `pytest`'s advisory
  is a dev-only, test-time exposure with no path into the deployed app.
- **No SQL injection surface**: every query goes through SQLAlchemy's ORM/query builder — nothing
  in this codebase interpolates a string into raw SQL.
- **Accepted trade-offs, unchanged from earlier phases**: JWTs are stateless with no server-side
  revocation list (`POST /auth/logout` is a client-side-only no-op — see `backend/README`'s Auth
  section); the rate limiter's state doesn't survive a restart or share across multiple worker
  processes. Both are documented, deliberate scope limits at this project's scale, not oversights.

## Documentation

- **Technical Design Document (Phase 1)** — architecture, database ERD, REST API spec, the
  skill-gap/recommendation algorithms, security model, testing strategy, and the full 12-phase
  delivery plan. (Published separately as the project's design artifact.)
- `backend/` and `frontend/` each grow their own more detailed README as their structure fills
  in — this root README stays focused on "how do I run the whole thing."

## Development phases

1. ✅ Requirements & architecture (Technical Design Document)
2. ✅ Project initialization
3. ✅ Database & authentication
4. ✅ Student profile
5. ✅ Resume system (upload, parsing, AI analysis)
6. ✅ Career & skill system (skill-gap analysis, career recommendations)
7. ✅ Learning resources & job matching
8. ✅ Interview preparation & mock interviews
9. ✅ Career dashboard
10. ✅ Admin panel
11. ✅ Testing & security hardening — **this phase**
12. ⬜ Deployment
