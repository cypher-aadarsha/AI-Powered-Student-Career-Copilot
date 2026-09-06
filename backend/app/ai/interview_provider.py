"""Interview-answer feedback: the same two-provider pattern as resume
analysis (app/ai/provider.py) — a deterministic heuristic by default, a
real LLM if `AI_PROVIDER=llm` is configured, with transparent fallback on
any failure. Kept as its own module rather than folded into AIProvider
since the shape genuinely differs (question+answer -> feedback+score, not
resume text+skills -> analysis) — see that module's docstring for the
resume-specific version of this same design.
"""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

MAX_SCORE = 100
STAR_KEYWORDS = ("situation", "task", "action", "result")


@dataclass
class AnswerFeedback:
    feedback: list[str]
    score: int
    provider_used: str


class InterviewFeedbackProvider(ABC):
    @abstractmethod
    def evaluate_answer(self, *, question_text: str, model_answer: str | None, answer_text: str) -> AnswerFeedback: ...


class MockInterviewFeedbackProvider(InterviewFeedbackProvider):
    """Deterministic, explainable scoring — no network calls. Checks
    length, whether the answer is backed by a concrete number, whether it
    follows the STAR structure (situation/task/action/result — useful for
    behavioral answers, harmless to check for technical ones too), and — if
    the question has a model answer — how much keyword overlap the answer
    has with it, as an explainable proxy for "did you cover the key ideas."
    """

    name = "mock"

    def evaluate_answer(self, *, question_text: str, model_answer: str | None, answer_text: str) -> AnswerFeedback:
        word_count = len(answer_text.split())
        feedback: list[str] = []
        score = 0

        if word_count < 20:
            feedback.append("Your answer is quite short — add more detail and a concrete example.")
        elif word_count <= 200:
            score += 30
            feedback.append("Good length — detailed without rambling.")
        else:
            score += 15
            feedback.append("Your answer is long — try to be more concise and focus on the key point.")

        if re.search(r"\d+%|\$\d|\b\d{2,}\b", answer_text):
            score += 20
            feedback.append("Nice — you backed your answer with a specific number.")
        else:
            feedback.append("Consider adding a specific metric or number to strengthen your answer.")

        star_hits = sum(1 for word in STAR_KEYWORDS if word in answer_text.lower())
        if star_hits >= 2:
            score += 25
            feedback.append("Your answer follows a clear structure (situation/action/result).")
        else:
            feedback.append("Structure your answer with the STAR method: Situation, Task, Action, Result.")

        if model_answer:
            model_keywords = {word.strip(".,()").lower() for word in model_answer.split() if len(word) > 4}
            answer_keywords = {word.strip(".,()").lower() for word in answer_text.split() if len(word) > 4}
            overlap_ratio = len(model_keywords & answer_keywords) / len(model_keywords) if model_keywords else 0.0
            score += round(25 * min(overlap_ratio * 2, 1.0))
            if overlap_ratio >= 0.2:
                feedback.append("Your answer touches on the key concepts expected for this question.")
            else:
                feedback.append("Your answer may be missing some of the key technical concepts here.")
        else:
            # No reference answer to compare against (typical for behavioral
            # questions) — don't penalize what can't be measured.
            score += 25

        score = max(0, min(MAX_SCORE, score))
        return AnswerFeedback(feedback=feedback, score=score, provider_used=self.name)


class LLMInterviewFeedbackProvider(InterviewFeedbackProvider):
    """Calls an OpenAI-chat-completions-compatible endpoint. Falls back to
    MockInterviewFeedbackProvider on any network or parsing failure so
    submitting an answer never fails just because the LLM is unreachable.
    """

    name = "llm"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._fallback = MockInterviewFeedbackProvider()

    def evaluate_answer(self, *, question_text: str, model_answer: str | None, answer_text: str) -> AnswerFeedback:
        try:
            return self._call_llm(question_text=question_text, model_answer=model_answer, answer_text=answer_text)
        except Exception:
            logger.exception("llm_interview_feedback_failed, falling back to heuristic provider")
            return self._fallback.evaluate_answer(
                question_text=question_text, model_answer=model_answer, answer_text=answer_text
            )

    def _call_llm(self, *, question_text: str, model_answer: str | None, answer_text: str) -> AnswerFeedback:
        prompt = (
            "You are an interview coach evaluating a candidate's answer. Respond with strict JSON only, "
            'shaped exactly as {"feedback": [str], "score": int 0-100}. feedback should be 2-4 short, '
            "actionable bullet points.\n\n"
            f"Question: {question_text}\n\n"
            f"Reference answer (for your evaluation only, not shown to the candidate): {model_answer or 'N/A'}\n\n"
            f"Candidate's answer:\n{answer_text[:3000]}"
        )
        response = httpx.post(
            f"{self._settings.llm_api_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self._settings.llm_api_key}"},
            json={
                "model": self._settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        return AnswerFeedback(
            feedback=[str(item) for item in data.get("feedback", [])],
            score=max(0, min(MAX_SCORE, int(data["score"]))),
            provider_used=self.name,
        )


def get_interview_feedback_provider(settings: Settings) -> InterviewFeedbackProvider:
    if settings.ai_provider == "llm" and settings.llm_api_key and settings.llm_api_base_url:
        return LLMInterviewFeedbackProvider(settings)
    return MockInterviewFeedbackProvider()
