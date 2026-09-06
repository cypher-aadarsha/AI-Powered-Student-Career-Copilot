import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.mock_interview import MockInterviewSession
from app.models.user import User
from app.schemas.interview import (
    MockInterviewAnswerResponse,
    MockInterviewSessionDetail,
    MockInterviewSessionListResponse,
    MockInterviewSessionResponse,
    MockInterviewSessionSummary,
    StartSessionRequest,
    SubmitAnswerRequest,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _service(db: Session) -> InterviewService:
    return InterviewService(db)


def _average_score(session: MockInterviewSession) -> int | None:
    scores = [answer.ai_score for answer in session.answers if answer.ai_score is not None]
    return round(sum(scores) / len(scores)) if scores else None


def _to_summary(session: MockInterviewSession) -> MockInterviewSessionSummary:
    return MockInterviewSessionSummary(
        id=session.id,
        career_role=session.career_role,
        status=session.status,
        question_count=len(session.questions),
        answered_count=len(session.answers),
        average_score=_average_score(session),
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


def _to_detail(session: MockInterviewSession) -> MockInterviewSessionDetail:
    return MockInterviewSessionDetail(
        id=session.id,
        career_role=session.career_role,
        status=session.status,
        questions=[sq.question for sq in session.questions],
        answers=list(session.answers),
        average_score=_average_score(session),
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


@router.post("/sessions", response_model=MockInterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewSessionResponse:
    session = _service(db).start_session(current_user.id, payload.career_role_id, payload.question_count)
    db.commit()
    db.refresh(session)
    return MockInterviewSessionResponse(data=_to_detail(session))


@router.get("/sessions", response_model=MockInterviewSessionListResponse)
def list_sessions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MockInterviewSessionListResponse:
    sessions = _service(db).list_sessions(current_user.id)
    return MockInterviewSessionListResponse(data=[_to_summary(session) for session in sessions])


@router.get("/sessions/{session_id}", response_model=MockInterviewSessionResponse)
def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewSessionResponse:
    session = _service(db).get_session(current_user.id, session_id)
    return MockInterviewSessionResponse(data=_to_detail(session))


@router.post(
    "/sessions/{session_id}/answers", response_model=MockInterviewAnswerResponse, status_code=status.HTTP_201_CREATED
)
def submit_answer(
    session_id: uuid.UUID,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewAnswerResponse:
    answer = _service(db).submit_answer(current_user.id, session_id, payload.question_id, payload.answer_text)
    db.commit()
    db.refresh(answer)
    return MockInterviewAnswerResponse(data=answer)
