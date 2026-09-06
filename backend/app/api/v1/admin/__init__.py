"""Admin-only routes (Phase 10) — split into one module per resource, as
this package's predecessor (a single admin.py placeholder) predicted it
eventually would. Every route here is guarded by require_role(UserRole.admin)
at this top-level router, so individual sub-routers never repeat the guard.
"""
from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.api.v1.admin import career_roles, interview_questions, job_postings, learning_resources, users
from app.models.user import UserRole

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(UserRole.admin))])

router.include_router(users.router)
router.include_router(career_roles.router)
router.include_router(learning_resources.router)
router.include_router(job_postings.router)
router.include_router(interview_questions.router)


@router.get("/ping")
def ping() -> dict:
    return {"data": {"status": "ok"}}
