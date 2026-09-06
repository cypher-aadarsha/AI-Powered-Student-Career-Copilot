"""AIProvider abstraction: the resume analyzer doesn't care whether the
implementation is a deterministic heuristic (MockAIProvider — the default,
needs no network access or API key) or a real LLM call (LLMAIProvider, used
when AI_PROVIDER=llm and an API key/base URL are configured). Swapping
providers never touches resume_service.py.
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

ACTION_VERBS = (
    "built", "led", "designed", "developed", "implemented", "created", "managed",
    "improved", "optimized", "launched", "automated", "deployed", "architected",
    "reduced", "increased", "delivered", "mentored", "researched",
)
SECTION_KEYWORDS = {
    "education": ("education", "university", "college", "bachelor"),
    "experience": ("experience", "internship", "employment"),
    "skills": ("skills", "technologies", "tech stack"),
    "projects": ("projects", "portfolio"),
}


@dataclass
class ResumeAnalysis:
    summary: str
    strengths: list[str]
    suggestions: list[str]
    score: int
    provider_used: str


class AIProvider(ABC):
    @abstractmethod
    def analyze_resume(self, *, text: str, detected_skills: list[str]) -> ResumeAnalysis: ...


class MockAIProvider(AIProvider):
    """Deterministic, explainable scoring — no network calls, so the app
    works fully offline. Every point awarded/withheld maps to one visible
    strength/suggestion, in keeping with the project's "explainable" goal
    rather than a black-box score.
    """

    name = "mock"

    def analyze_resume(self, *, text: str, detected_skills: list[str]) -> ResumeAnalysis:
        lowered = text.lower()
        word_count = len(text.split())

        strengths: list[str] = []
        suggestions: list[str] = []
        score = 0

        if 150 <= word_count <= 1200:
            score += 20
            strengths.append("Resume length is in a readable range.")
        elif word_count < 150:
            suggestions.append("Your resume looks very short — add more detail on projects and experience.")
        else:
            suggestions.append("Your resume is quite long — consider tightening it to the most relevant points.")

        found_sections = [section for section, kws in SECTION_KEYWORDS.items() if any(k in lowered for k in kws)]
        score += min(len(found_sections), 4) * 10
        if "skills" in found_sections:
            strengths.append("A dedicated skills section was found.")
        else:
            suggestions.append('Add a clear "Skills" section so it\'s easy to scan.')
        if "projects" in found_sections:
            strengths.append("Projects are called out explicitly.")
        else:
            suggestions.append('Add a "Projects" section — concrete work speaks louder than a skills list alone.')
        if "experience" not in found_sections:
            suggestions.append(
                "No work/internship experience section detected — add one even if it's coursework or freelance."
            )

        if len(detected_skills) >= 5:
            score += 20
            strengths.append(f"{len(detected_skills)} recognizable skills found in the text.")
        elif detected_skills:
            score += 10
        else:
            suggestions.append("No catalogue skills were detected — make sure skill names are spelled out explicitly.")

        verb_hits = sum(1 for verb in ACTION_VERBS if re.search(rf"\b{verb}\b", lowered))
        if verb_hits >= 3:
            score += 15
            strengths.append("Bullet points use strong action verbs.")
        else:
            suggestions.append('Start bullet points with action verbs (e.g. "built", "led", "improved").')

        if re.search(r"\d+%|\$\d|\b\d{2,}\b", text):
            score += 15
            strengths.append("Includes quantified results (numbers, percentages).")
        else:
            suggestions.append('Quantify your impact where possible (e.g. "reduced load time by 30%").')

        if re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", lowered):
            score += 10
        else:
            suggestions.append("Include an email address so recruiters can reach you.")

        score = max(0, min(MAX_SCORE, score))
        summary = (
            f"This resume covers {len(found_sections)} of {len(SECTION_KEYWORDS)} expected sections and references "
            f"{len(detected_skills)} recognized skill(s) from the catalogue. Overall score: {score}/100."
        )
        return ResumeAnalysis(
            summary=summary,
            strengths=strengths or ["Resume received — add more content for a deeper analysis."],
            suggestions=suggestions,
            score=score,
            provider_used=self.name,
        )


class LLMAIProvider(AIProvider):
    """Calls an OpenAI-chat-completions-compatible endpoint. Falls back to
    MockAIProvider on any network or parsing failure so an upload never
    fails just because the LLM is unreachable or returns malformed JSON.
    """

    name = "llm"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._fallback = MockAIProvider()

    def analyze_resume(self, *, text: str, detected_skills: list[str]) -> ResumeAnalysis:
        try:
            return self._call_llm(text=text, detected_skills=detected_skills)
        except Exception:
            logger.exception("llm_resume_analysis_failed, falling back to heuristic provider")
            return self._fallback.analyze_resume(text=text, detected_skills=detected_skills)

    def _call_llm(self, *, text: str, detected_skills: list[str]) -> ResumeAnalysis:
        prompt = (
            "You are a career coach reviewing a student's resume. Respond with strict JSON only, "
            'shaped exactly as {"summary": str, "strengths": [str], "suggestions": [str], "score": int 0-100}.\n\n'
            f"Detected catalogue skills: {', '.join(detected_skills) or 'none'}\n\n"
            f"Resume text:\n{text[:6000]}"
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
        return ResumeAnalysis(
            summary=str(data["summary"]),
            strengths=[str(s) for s in data.get("strengths", [])],
            suggestions=[str(s) for s in data.get("suggestions", [])],
            score=max(0, min(MAX_SCORE, int(data["score"]))),
            provider_used=self.name,
        )


def get_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "llm" and settings.llm_api_key and settings.llm_api_base_url:
        return LLMAIProvider(settings)
    return MockAIProvider()
