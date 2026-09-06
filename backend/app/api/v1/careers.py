import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.career import CareerDetail, CareerDetailResponse, CareerListItem, CareerListResponse, MatchedSkill
from app.schemas.learning import RoleLearningPlan, RoleLearningPlanResponse, SkillWithResources
from app.services.career_service import CareerService
from app.services.learning_service import LearningService

router = APIRouter(prefix="/careers", tags=["careers"])


def _service(db: Session) -> CareerService:
    return CareerService(db)


@router.get("", response_model=CareerListResponse)
def list_careers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CareerListResponse:
    ranked = _service(db).list_roles_ranked(current_user.id)
    data = [
        CareerListItem(
            role=role,
            score=gap.score,
            matched_required=gap.total_required - len(gap.missing_required),
            total_required=gap.total_required,
            matched_preferred=gap.total_preferred - len(gap.missing_preferred),
            total_preferred=gap.total_preferred,
        )
        for role, gap in ranked
    ]
    return CareerListResponse(data=data)


@router.get("/{role_id}", response_model=CareerDetailResponse)
def get_career_detail(
    role_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CareerDetailResponse:
    role, gap = _service(db).get_role_detail(current_user.id, role_id)
    detail = CareerDetail(
        role=role,
        score=gap.score,
        matched_skills=[
            MatchedSkill(skill=skill, proficiency_level=level) for skill, level in gap.matched_skills
        ],
        missing_required_skills=list(gap.missing_required),
        missing_preferred_skills=list(gap.missing_preferred),
        summary=gap.summary,
    )
    return CareerDetailResponse(data=detail)


@router.get("/{role_id}/learning-plan", response_model=RoleLearningPlanResponse)
def get_role_learning_plan(
    role_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoleLearningPlanResponse:
    role, missing_required, missing_preferred = LearningService(db).get_role_learning_plan(current_user.id, role_id)
    plan = RoleLearningPlan(
        role=role,
        missing_required=[SkillWithResources(skill=skill, resources=resources) for skill, resources in missing_required],
        missing_preferred=[
            SkillWithResources(skill=skill, resources=resources) for skill, resources in missing_preferred
        ],
    )
    return RoleLearningPlanResponse(data=plan)
