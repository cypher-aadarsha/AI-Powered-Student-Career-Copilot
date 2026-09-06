# AI-Powered Student Career Copilot

A career-readiness platform for university/college students: upload a resume, pick a target
career role, get an explainable skill-gap score, and work through a personalized learning,
job-matching, and interview-prep roadmap.

BSc. CSIT 6th Semester Software Engineering project — built as a production-quality, modular
monolith rather than a toy CRUD demo. The full architecture, database design, algorithms, and
phased delivery plan are documented in the **Technical Design Document** (Phase 1 deliverable).

**Status:** Phase 5 — Resume System. On top of profile management (Phase 4), a student can
upload a PDF/DOCX resume and get it parsed (contact info, links, catalogue skills detected in
the text) and analyzed by a pluggable AI layer: a deterministic, fully-explainable heuristic
provider by default, or a real LLM if one is configured. Every other feature module lands in
the phases that follow.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, React Hook Form + Zod |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic migrations |
| AI/NLP | pdfplumber, python-docx (Phase 5); sentence-transformers/spaCy planned for Phase 6's semantic skill-gap matching |
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

Then open:
- **Frontend:** http://localhost:3000 — register an account, log in, fill in your profile at
  `/profile`, and upload a resume for parsing + AI analysis at `/resume`.
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
# Backend — 44 tests: health, auth (hashing, registration, login, JWT-gated routes, RBAC),
# the profile module (core fields, skills with case-insensitive dedup, projects with skill
# tagging, experiences, certifications, cross-user ownership checks), and the resume module
# (PDF/DOCX upload + parsing, contact-info/skill extraction, the heuristic AI analyzer,
# file-type/size validation, ownership scoping). Runs against a disposable in-memory SQLite
# DB, no Postgres needed.
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
5. ✅ Resume system (upload, parsing, AI analysis) — **this phase**
6. ⬜ Career & skill system (skill-gap analysis, career recommendations)
7. ⬜ Learning resources & job matching
8. ⬜ Interview preparation & mock interviews
9. ⬜ Career dashboard
10. ⬜ Admin panel
11. ⬜ Testing & security hardening
12. ⬜ Deployment
