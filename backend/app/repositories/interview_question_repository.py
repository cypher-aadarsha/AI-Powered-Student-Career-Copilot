import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import (
    InterviewQuestion,
    InterviewQuestionSkill,
    QuestionCategory,
    QuestionDifficulty,
)


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

    def create(
        self,
        *,
        question_text: str,
        category: QuestionCategory,
        difficulty: QuestionDifficulty,
        model_answer: str | None,
    ) -> InterviewQuestion:
        question = InterviewQuestion(
            question_text=question_text, category=category, difficulty=difficulty, model_answer=model_answer
        )
        self.db.add(question)
        self.db.flush()
        return question

    def update(
        self,
        question: InterviewQuestion,
        *,
        question_text: str,
        category: QuestionCategory,
        difficulty: QuestionDifficulty,
        model_answer: str | None,
    ) -> InterviewQuestion:
        question.question_text = question_text
        question.category = category
        question.difficulty = difficulty
        question.model_answer = model_answer
        self.db.flush()
        return question

    def delete(self, question: InterviewQuestion) -> None:
        self.db.delete(question)

    def set_skills(self, question: InterviewQuestion, skill_ids: list[uuid.UUID]) -> None:
        for existing in list(question.skills):
            self.db.delete(existing)
        self.db.flush()
        for skill_id in dict.fromkeys(skill_ids):
            self.db.add(InterviewQuestionSkill(interview_question_id=question.id, skill_id=skill_id))
        self.db.flush()
