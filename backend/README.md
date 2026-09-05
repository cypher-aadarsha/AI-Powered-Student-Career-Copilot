# Career Copilot — Backend

FastAPI + SQLAlchemy + PostgreSQL. See the repo root `README.md` for how to run the full stack
via Docker Compose.

## Standalone commands

```bash
python -m venv .venv && .venv/Scripts/activate   # source .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head              # creates the schema against DATABASE_URL
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
  models/        SQLAlchemy models — user.py (Phase 3); more land with each phase's data
  schemas/       Pydantic request/response models
  services/      Business logic — routers never hash a password or query the DB directly
  repositories/  Query objects — the only layer that writes SQLAlchemy queries
  ai/            AIProvider interface + implementations (added Phase 5)
migrations/      Alembic — versions/0001_create_users_table.py is the first migration
seed/            Seed/demo data loaders (added Phase 6+)
tests/           pytest — conftest.py's `client` fixture runs against a disposable in-memory
                 SQLite DB (models use dialect-generic types for exactly this reason), so the
                 suite needs no live Postgres
```

`ai/` and `seed/` are intentionally still empty — they fill in starting Phase 5 and Phase 6.

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
