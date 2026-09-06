"""Mock interview sessions (Phase 8): pick a fixed question set once at
session start (mixing behavioral/situational questions with technical ones
leaning toward a chosen career role's skills, if any), then score each
submitted answer through the same explainable-heuristic-by-default /
LLM-if-configured pattern the resume analyzer uses.
"""
import random
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.interview_provider import get_interview_feedback_provider
from app.core.config import Settings, get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.models.interview_question import InterviewQuestion, QuestionCategory
from app.models.mock_interview import MockInterviewAnswer, MockInterviewSession, SessionStatus
from app.repositories.career_role_repository import CareerRoleRepository
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.mock_interview_repository import MockInterviewAnswerRepository, MockInterviewSessionRepository
from app.repositories.profile_repository import ProfileRepository


class InterviewService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.profiles = ProfileRepository(db)
        self.questions = InterviewQuestionRepository(db)
        self.career_roles = CareerRoleRepository(db)
        self.sessions = MockInterviewSessionRepository(db)
        self.answers = MockInterviewAnswerRepository(db)

    def start_session(
        self, user_id: uuid.UUID, career_role_id: uuid.UUID | None, question_count: int
    ) -> MockInterviewSession:
        profile = self._get_or_create_profile(user_id)

        career_role = None
        if career_role_id is not None:
            career_role = self.career_roles.get_by_id(career_role_id)
            if career_role is None:
                raise NotFoundError("Career role not found.")

        questions = self._select_questions(career_role, question_count)
        session = self.sessions.create(student_profile_id=profile.id, career_role_id=career_role_id)
        self.sessions.assign_questions(session, questions)
        return session

    def list_sessions(self, user_id: uuid.UUID) -> list[MockInterviewSession]:
        profile = self._get_or_create_profile(user_id)
        return self.sessions.list_by_profile(profile.id)

    def get_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> MockInterviewSession:
        return self._get_owned_session(user_id, session_id)

    def submit_answer(
        self, user_id: uuid.UUID, session_id: uuid.UUID, question_id: uuid.UUID, answer_text: str
    ) -> MockInterviewAnswer:
        session = self._get_owned_session(user_id, session_id)

        assigned = next((sq.question for sq in session.questions if sq.question_id == question_id), None)
        if assigned is None:
            raise NotFoundError("This question is not part of the session.")
        if self.answers.get_existing(session.id, question_id) is not None:
            raise ConflictError("You've already answered this question.")

        provider = get_interview_feedback_provider(self.settings)
        result = provider.evaluate_answer(
            question_text=assigned.question_text, model_answer=assigned.model_answer, answer_text=answer_text
        )
        answer = self.answers.create(
            session_id=session.id,
            question_id=question_id,
            answer_text=answer_text,
            ai_feedback=result.feedback,
            ai_score=result.score,
            ai_provider_used=result.provider_used,
        )
        self.db.flush()
        self._maybe_complete_session(session)
        return answer

    # --- internals -----------------------------------------------------

    def _get_or_create_profile(self, user_id: uuid.UUID):
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            profile = self.profiles.create(user_id=user_id)
        return profile

    def _get_owned_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> MockInterviewSession:
        profile = self._get_or_create_profile(user_id)
        session = self.sessions.get_by_id(session_id)
        if session is None or session.student_profile_id != profile.id:
            raise NotFoundError("Interview session not found.")
        return session

    def _select_questions(self, career_role, question_count: int) -> list[InterviewQuestion]:
        non_technical_pool = self.questions.list_by_category(
            QuestionCategory.behavioral
        ) + self.questions.list_by_category(QuestionCategory.situational)
        technical_pool = self.questions.list_by_category(QuestionCategory.technical)

        if career_role is not None:
            role_skill_ids = {rs.skill_id for rs in career_role.skills}
            role_specific = [q for q in technical_pool if any(s.skill_id in role_skill_ids for s in q.skills)]
            if role_specific:
                technical_pool = role_specific

        non_technical_count = max(1, question_count // 3)
        technical_count = question_count - non_technical_count

        selected = random.sample(non_technical_pool, min(non_technical_count, len(non_technical_pool)))
        selected += random.sample(technical_pool, min(technical_count, len(technical_pool)))
        random.shuffle(selected)
        return selected

    def _maybe_complete_session(self, session: MockInterviewSession) -> None:
        assigned_ids = {sq.question_id for sq in session.questions}
        answered_ids = {answer.question_id for answer in session.answers}
        if assigned_ids and answered_ids >= assigned_ids:
            session.status = SessionStatus.completed
            session.completed_at = datetime.now(timezone.utc)
            self.db.flush()
