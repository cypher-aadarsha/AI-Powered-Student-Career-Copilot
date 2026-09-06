import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.interview_question import InterviewQuestion
from app.schemas.admin import (
    AdminInterviewQuestionListResponse,
    AdminInterviewQuestionPublic,
    AdminInterviewQuestionResponse,
    AdminInterviewQuestionWriteRequest,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/interview-questions")


def _to_public(question: InterviewQuestion) -> AdminInterviewQuestionPublic:
    return AdminInterviewQuestionPublic(
        id=question.id,
        question_text=question.question_text,
        category=question.category,
        difficulty=question.difficulty,
        model_answer=question.model_answer,
        skills=[qs.skill for qs in question.skills],
    )


@router.get("", response_model=AdminInterviewQuestionListResponse)
def list_interview_questions(db: Session = Depends(get_db)) -> AdminInterviewQuestionListResponse:
    questions = AdminService(db).list_interview_questions()
    return AdminInterviewQuestionListResponse(data=[_to_public(question) for question in questions])


@router.post("", response_model=AdminInterviewQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_interview_question(
    payload: AdminInterviewQuestionWriteRequest, db: Session = Depends(get_db)
) -> AdminInterviewQuestionResponse:
    question = AdminService(db).create_interview_question(payload)
    db.commit()
    db.refresh(question)
    return AdminInterviewQuestionResponse(data=_to_public(question))


@router.put("/{question_id}", response_model=AdminInterviewQuestionResponse)
def update_interview_question(
    question_id: uuid.UUID, payload: AdminInterviewQuestionWriteRequest, db: Session = Depends(get_db)
) -> AdminInterviewQuestionResponse:
    question = AdminService(db).update_interview_question(question_id, payload)
    db.commit()
    db.refresh(question)
    return AdminInterviewQuestionResponse(data=_to_public(question))


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_question(question_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    AdminService(db).delete_interview_question(question_id)
    db.commit()
