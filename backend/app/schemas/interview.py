"""Request/response shapes for the mock-interview module (Phase 8).
`average_score` is never stored — routes compute it from `answers` at
response time, same reasoning as the career module's on-the-fly scoring:
there's nothing to keep in sync with a cache.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.interview_question import QuestionCategory, QuestionDifficulty
from app.models.mock_interview import SessionStatus
from app.schemas.career import CareerRoleSummary
from app.schemas.profile import SkillPublic


class InterviewQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_text: str
    category: QuestionCategory
    difficulty: QuestionDifficulty
    skills: list[SkillPublic]

    @field_validator("skills", mode="before")
    @classmethod
    def _unwrap_question_skills(cls, value):
        # InterviewQuestion.skills is a list of InterviewQuestionSkill join
        # rows; unwrap to the underlying Skill, same pattern as
        # ProjectPublic._unwrap_project_skills in schemas/profile.py.
        return [item.skill if hasattr(item, "skill") else item for item in value]


class MockInterviewAnswerPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    answer_text: str
    ai_feedback: list[str] | None
    ai_score: int | None
    ai_provider_used: str | None
    created_at: datetime


class MockInterviewAnswerResponse(BaseModel):
    data: MockInterviewAnswerPublic


class StartSessionRequest(BaseModel):
    career_role_id: uuid.UUID | None = None
    question_count: int = Field(default=5, ge=3, le=10)


class SubmitAnswerRequest(BaseModel):
    question_id: uuid.UUID
    answer_text: str = Field(min_length=10, max_length=4000)


class MockInterviewSessionSummary(BaseModel):
    id: uuid.UUID
    career_role: CareerRoleSummary | None
    status: SessionStatus
    question_count: int
    answered_count: int
    average_score: int | None
    created_at: datetime
    completed_at: datetime | None


class MockInterviewSessionListResponse(BaseModel):
    data: list[MockInterviewSessionSummary]


class MockInterviewSessionDetail(BaseModel):
    id: uuid.UUID
    career_role: CareerRoleSummary | None
    status: SessionStatus
    questions: list[InterviewQuestionPublic]
    answers: list[MockInterviewAnswerPublic]
    average_score: int | None
    created_at: datetime
    completed_at: datetime | None


class MockInterviewSessionResponse(BaseModel):
    data: MockInterviewSessionDetail
