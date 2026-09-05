"""Admin-only routes. This file is a placeholder proving the require_role
guard end-to-end; the real CRUD surfaces (users, career roles, skills,
resources, jobs, questions — see TDD module M14) land in Phase 10 and will
likely split this into an admin/ subpackage.
"""
from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
def ping(_: User = Depends(require_role(UserRole.admin))) -> dict:
    return {"data": {"status": "ok"}}
