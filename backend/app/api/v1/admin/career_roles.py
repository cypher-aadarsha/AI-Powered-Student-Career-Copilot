import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.career_role import CareerRole, RoleSkillImportance
from app.schemas.admin import AdminCareerRolePublic, AdminCareerRoleListResponse, AdminCareerRoleResponse, AdminCareerRoleWriteRequest
from app.services.admin_service import AdminService

router = APIRouter(prefix="/career-roles")


def _to_public(role: CareerRole) -> AdminCareerRolePublic:
    return AdminCareerRolePublic(
        id=role.id,
        title=role.title,
        description=role.description,
        required_skills=[rs.skill for rs in role.skills if rs.importance == RoleSkillImportance.required],
        preferred_skills=[rs.skill for rs in role.skills if rs.importance == RoleSkillImportance.preferred],
    )


@router.get("", response_model=AdminCareerRoleListResponse)
def list_career_roles(db: Session = Depends(get_db)) -> AdminCareerRoleListResponse:
    roles = AdminService(db).list_career_roles()
    return AdminCareerRoleListResponse(data=[_to_public(role) for role in roles])


@router.post("", response_model=AdminCareerRoleResponse, status_code=status.HTTP_201_CREATED)
def create_career_role(payload: AdminCareerRoleWriteRequest, db: Session = Depends(get_db)) -> AdminCareerRoleResponse:
    role = AdminService(db).create_career_role(payload)
    db.commit()
    db.refresh(role)
    return AdminCareerRoleResponse(data=_to_public(role))


@router.put("/{role_id}", response_model=AdminCareerRoleResponse)
def update_career_role(
    role_id: uuid.UUID, payload: AdminCareerRoleWriteRequest, db: Session = Depends(get_db)
) -> AdminCareerRoleResponse:
    role = AdminService(db).update_career_role(role_id, payload)
    db.commit()
    db.refresh(role)
    return AdminCareerRoleResponse(data=_to_public(role))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_career_role(role_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    AdminService(db).delete_career_role(role_id)
    db.commit()
