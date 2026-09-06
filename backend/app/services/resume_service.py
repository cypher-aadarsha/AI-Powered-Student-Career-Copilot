"""Resume upload, parsing, and AI analysis. Processing runs synchronously
inside the upload request — there is no background job queue in this stack
yet, so a large file adds a few hundred ms to the response. That's an
accepted trade-off at this scale, not a gap: see backend/README's Phase 5
section for the known limitation and what a queue-based version would add.
"""
import logging
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.ai.extraction import detect_skills, extract_contact_info
from app.ai.parsing import UnsupportedResumeFormat, extract_text
from app.ai.provider import get_ai_provider
from app.core.config import Settings, get_settings
from app.core.exceptions import AppError, NotFoundError
from app.models.resume import Resume, ResumeStatus
from app.models.student_profile import StudentProfile
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.skill_repository import SkillRepository

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class UnsupportedFileTypeError(AppError):
    def __init__(self):
        super().__init__("Only PDF and DOCX resumes are supported.", status_code=422, code="unsupported_file_type")


class FileTooLargeError(AppError):
    def __init__(self, max_mb: int):
        super().__init__(f"Resume file exceeds the {max_mb}MB limit.", status_code=422, code="file_too_large")


class ResumeService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.profiles = ProfileRepository(db)
        self.resumes = ResumeRepository(db)
        self.skills = SkillRepository(db)

    def list_resumes(self, user_id: uuid.UUID) -> list[Resume]:
        profile = self._get_or_create_profile(user_id)
        return self.resumes.list_by_profile(profile.id)

    def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        profile = self._get_or_create_profile(user_id)
        resume = self.resumes.get_by_id(resume_id)
        if resume is None or resume.student_profile_id != profile.id:
            raise NotFoundError("Resume not found on your profile.")
        return resume

    def upload_resume(self, user_id: uuid.UUID, upload: UploadFile) -> Resume:
        profile = self._get_or_create_profile(user_id)

        mime_type = upload.content_type or ""
        if mime_type not in ALLOWED_MIME_TYPES:
            raise UnsupportedFileTypeError()

        file_bytes = upload.file.read()
        max_bytes = self.settings.resume_max_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise FileTooLargeError(self.settings.resume_max_size_mb)

        storage_path = self._save_file(profile.id, upload.filename or "resume", file_bytes)
        resume = self.resumes.create(
            student_profile_id=profile.id,
            original_filename=upload.filename or "resume",
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=len(file_bytes),
        )
        self.db.flush()
        self._process(resume, file_bytes, mime_type)
        return resume

    def reanalyze_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        resume = self.get_resume(user_id, resume_id)
        if not resume.raw_text:
            raise AppError("This resume hasn't been parsed yet.", status_code=409, code="not_parsed")
        self._analyze(resume)
        return resume

    def delete_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> None:
        resume = self.get_resume(user_id, resume_id)
        file_path = Path(resume.storage_path)
        self.resumes.delete(resume)
        self.db.flush()
        if file_path.exists():
            file_path.unlink(missing_ok=True)

    # --- internals -----------------------------------------------------

    def _get_or_create_profile(self, user_id: uuid.UUID) -> StudentProfile:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            profile = self.profiles.create(user_id=user_id)
        return profile

    def _save_file(self, profile_id: uuid.UUID, original_filename: str, file_bytes: bytes) -> str:
        extension = Path(original_filename).suffix
        directory = Path(self.settings.resume_storage_dir) / str(profile_id)
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{uuid.uuid4()}{extension}"
        file_path.write_bytes(file_bytes)
        return str(file_path)

    def _process(self, resume: Resume, file_bytes: bytes, mime_type: str) -> None:
        resume.status = ResumeStatus.parsing
        self.db.flush()
        try:
            text = extract_text(file_bytes, mime_type)
        except UnsupportedResumeFormat as exc:
            resume.status = ResumeStatus.failed
            resume.parse_error = exc.message
            self.db.flush()
            return
        except Exception:
            logger.exception("resume_parse_failed resume_id=%s", resume.id)
            resume.status = ResumeStatus.failed
            resume.parse_error = "Couldn't read this file — it may be corrupted or password-protected."
            self.db.flush()
            return

        resume.raw_text = text
        catalogue_names = [skill.name for skill in self.skills.search(limit=1000)]
        contact_info = extract_contact_info(text)
        detected_skills = detect_skills(text, catalogue_names)
        resume.parsed_data = {**contact_info, "detected_skills": detected_skills}
        resume.status = ResumeStatus.parsed
        self.db.flush()
        self._analyze(resume)

    def _analyze(self, resume: Resume) -> None:
        detected_skills = (resume.parsed_data or {}).get("detected_skills", [])
        provider = get_ai_provider(self.settings)
        result = provider.analyze_resume(text=resume.raw_text or "", detected_skills=detected_skills)
        resume.ai_summary = result.summary
        resume.ai_strengths = result.strengths
        resume.ai_suggestions = result.suggestions
        resume.ai_score = result.score
        resume.ai_provider_used = result.provider_used
        self.db.flush()
