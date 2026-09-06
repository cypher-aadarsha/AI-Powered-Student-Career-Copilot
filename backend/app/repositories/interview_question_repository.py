import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion, QuestionCategory


class InterviewQuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_category(self, category: QuestionCategory) -> list[InterviewQuestion]:
        stmt = select(InterviewQuestion).where(InterviewQuestion.category == category)
        return list(self.db.scalars(stmt))

    def list_all(self) -> list[InterviewQuestion]:
        return list(self.db.scalars(select(InterviewQuestion)))

    def get_by_id(self, question_id: uuid.UUID) -> InterviewQuestion | None:
        return self.db.get(InterviewQuestion, question_id)
