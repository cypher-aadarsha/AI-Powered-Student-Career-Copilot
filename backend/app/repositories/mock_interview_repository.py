import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion
from app.models.mock_interview import MockInterviewAnswer, MockInterviewSession, MockInterviewSessionQuestion


class MockInterviewSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_profile(self, student_profile_id: uuid.UUID) -> list[MockInterviewSession]:
        stmt = (
            select(MockInterviewSession)
            .where(MockInterviewSession.student_profile_id == student_profile_id)
            .order_by(MockInterviewSession.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_by_id(self, session_id: uuid.UUID) -> MockInterviewSession | None:
        return self.db.get(MockInterviewSession, session_id)

    def create(
        self, *, student_profile_id: uuid.UUID, career_role_id: uuid.UUID | None
    ) -> MockInterviewSession:
        session = MockInterviewSession(student_profile_id=student_profile_id, career_role_id=career_role_id)
        self.db.add(session)
        self.db.flush()
        return session

    def assign_questions(self, session: MockInterviewSession, questions: list[InterviewQuestion]) -> None:
        for index, question in enumerate(questions):
            self.db.add(
                MockInterviewSessionQuestion(session_id=session.id, question_id=question.id, order_index=index)
            )
        self.db.flush()


class MockInterviewAnswerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_existing(self, session_id: uuid.UUID, question_id: uuid.UUID) -> MockInterviewAnswer | None:
        stmt = select(MockInterviewAnswer).where(
            MockInterviewAnswer.session_id == session_id, MockInterviewAnswer.question_id == question_id
        )
        return self.db.scalar(stmt)

    def create(
        self,
        *,
        session_id: uuid.UUID,
        question_id: uuid.UUID,
        answer_text: str,
        ai_feedback: list[str],
        ai_score: int,
        ai_provider_used: str,
    ) -> MockInterviewAnswer:
        answer = MockInterviewAnswer(
            session_id=session_id,
            question_id=question_id,
            answer_text=answer_text,
            ai_feedback=ai_feedback,
            ai_score=ai_score,
            ai_provider_used=ai_provider_used,
        )
        self.db.add(answer)
        self.db.flush()
        return answer
