import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.certification import Certification


class CertificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_profile(self, student_profile_id: uuid.UUID) -> list[Certification]:
        stmt = (
            select(Certification)
            .where(Certification.student_profile_id == student_profile_id)
            .order_by(Certification.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_by_id(self, certification_id: uuid.UUID) -> Certification | None:
        return self.db.get(Certification, certification_id)

    def create(
        self,
        *,
        student_profile_id: uuid.UUID,
        name: str,
        issuer: str | None,
        issue_date: date | None,
        credential_url: str | None,
    ) -> Certification:
        certification = Certification(
            student_profile_id=student_profile_id,
            name=name,
            issuer=issuer,
            issue_date=issue_date,
            credential_url=credential_url,
        )
        self.db.add(certification)
        self.db.flush()
        return certification

    def update(
        self,
        certification: Certification,
        *,
        name: str,
        issuer: str | None,
        issue_date: date | None,
        credential_url: str | None,
    ) -> Certification:
        certification.name = name
        certification.issuer = issuer
        certification.issue_date = issue_date
        certification.credential_url = credential_url
        self.db.flush()
        return certification

    def delete(self, certification: Certification) -> None:
        self.db.delete(certification)
