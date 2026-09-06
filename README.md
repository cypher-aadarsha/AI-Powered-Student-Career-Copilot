# AI-Powered Student Career Copilot

A career-readiness platform for university/college students: upload a resume, pick a target
career role, get an explainable skill-gap score, and work through a personalized learning,
job-matching, and interview-prep roadmap.

BSc. CSIT 6th Semester Software Engineering project — built as a production-quality, modular
monolith rather than a toy CRUD demo. The full architecture, database design, algorithms, and
phased delivery plan are documented in the **Technical Design Document** (Phase 1 deliverable).

**Status:** Phase 10 — Admin Panel. The four platform-curated catalogues every earlier phase
deliberately left read-only (career roles, learning resources, job postings, interview questions)
now have full admin CRUD at `/admin`, plus user moderation (deactivate/reactivate an account).
Admin accounts are provisioned out-of-band via a seed script, never through self-registration.
Every other feature module lands in the phases that follow.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, React Hook Form + Zod |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic migrations |
| AI/NLP | pdfplumber, python-docx (Phase 5); skill-gap matching (Phase 6/7) is a deterministic weighted formula, not embeddings — see backend/README |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| DevOps | Docker, Docker Compose, pytest, Jest |

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
# Backend — 114 tests: health, auth (hashing, registration, login, JWT-gated routes, RBAC),
# the profile module (core fields, skills with case-insensitive dedup, projects with skill
# tagging, experiences, certifications, cross-user ownership checks), the resume module
# (PDF/DOCX upload + parsing, contact-info/skill extraction, the heuristic AI analyzer,
# file-type/size validation, ownership scoping), the career module (skill-gap scoring
# formula, ranked recommendations, per-role detail, seed-script idempotency), the
# learning/job modules (resource browsing + skill filter, the role learning-plan endpoint,
# job-posting ranking reusing the same skill-gap engine), the interview module (role-aware
# question selection, one-answer-per-question, auto-completion, the heuristic feedback
# provider's scoring rules), the dashboard module (profile-completion scoring, latest
# resume, top matches, interview stats, the suggested-actions rules), and the admin module
# (role-guard enforcement, CRUD over all four catalogues, user moderation including the
# can't-deactivate-yourself guard, and the delete-blocked-when-in-use conflict path — which
# is also why the test DB now runs with SQLite's FOREIGN KEY enforcement turned on, see
# tests/conftest.py). Runs against a disposable in-memory SQLite DB, no Postgres needed.
cd backend && pytest -v

# Frontend build + lint
cd frontend && npm run build && npm run lint
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example` — every variable the app reads is
documented there. Never commit `.env` / `.env.local`; only the `.env.example` templates are
version-controlled.

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
10. ✅ Admin panel — **this phase**
11. ⬜ Testing & security hardening
12. ⬜ Deployment
