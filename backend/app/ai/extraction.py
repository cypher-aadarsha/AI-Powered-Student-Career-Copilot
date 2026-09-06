"""Rule-based structured-data extraction from resume text: contact links
and skills matched against the shared skill catalogue. This is deliberately
not ML/embeddings-based — Phase 6's skill-gap matching is where semantic
similarity earns its keep; here we only need "does this exact skill name
literally appear in the text," which a plain word-boundary match answers
and keeps this phase's AI pipeline fully explainable.
"""
import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\-.\s()]{7,}\d")
URL_RE = re.compile(r"https?://[^\s,)]+", re.IGNORECASE)


def extract_contact_info(text: str) -> dict:
    emails = sorted(set(EMAIL_RE.findall(text)))
    phones = sorted(set(m.strip() for m in PHONE_RE.findall(text)))
    urls = sorted(set(URL_RE.findall(text)))
    github_url = next((u for u in urls if "github.com" in u.lower()), None)
    linkedin_url = next((u for u in urls if "linkedin.com" in u.lower()), None)
    return {
        "emails": emails,
        "phones": phones,
        "urls": urls,
        "github_url": github_url,
        "linkedin_url": linkedin_url,
    }


def detect_skills(text: str, catalogue_names: list[str]) -> list[str]:
    """Case-insensitive word-boundary match of each catalogue skill name
    against the resume text. Skill names can contain punctuation (e.g.
    "C++", "Node.js"), so boundaries are checked against non-alphanumeric
    neighbors rather than assuming `\\b` (which treats `+` as a boundary
    character anyway, but this is explicit and easier to reason about).
    """
    lowered = text.lower()
    matches: list[str] = []
    for name in catalogue_names:
        pattern = re.escape(name.strip().lower())
        if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", lowered):
            matches.append(name)
    return matches
