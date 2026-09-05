# Career Copilot — Backend

FastAPI + SQLAlchemy + PostgreSQL. See the repo root `README.md` for how to run the full stack
via Docker Compose.

## Standalone commands

```bash
python -m venv .venv && .venv/Scripts/activate   # source .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload    # http://localhost:8000 — docs at /docs
pytest -v
```

## Structure

```
app/
  core/          Settings, logging, exception → HTTP mapping
  api/v1/        Routers — thin, delegate to services/
  db/            Engine/session + declarative base
  models/        SQLAlchemy models (added Phase 3)
  schemas/       Pydantic request/response models (added Phase 3+)
  services/      Business logic (added Phase 3+)
  repositories/  Query objects (added Phase 3+)
  ai/            AIProvider interface + implementations (added Phase 5)
migrations/      Alembic (added Phase 3)
seed/            Seed/demo data loaders (added Phase 6+)
tests/           pytest — unit + integration
```

`models/`, `schemas/`, `services/`, `repositories/`, `ai/`, and `migrations/` are intentionally
absent until the phase that needs them (Phase 3 — Database & Auth is next) — see the Technical
Design Document's Backend Folder Structure section for the target layout.
