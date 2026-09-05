import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.experience import EmploymentType, Experience


class ExperienceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_profile(self, student_profile_id: uuid.UUID) -> list[Experience]:
        stmt = (
            select(Experience)
            .where(Experience.student_profile_id == student_profile_id)
            .order_by(Experience.start_date.desc())
        )
        return list(self.db.scalars(stmt))

    def get_by_id(self, experience_id: uuid.UUID) -> Experience | None:
        return self.db.get(Experience, experience_id)

    def create(
        self,
        *,
        student_profile_id: uuid.UUID,
        title: str,
        company: str,
        employment_type: EmploymentType,
        start_date: date,
        end_date: date | None,
        is_current: bool,
        description: str | None,
    ) -> Experience:
        experience = Experience(
            student_profile_id=student_profile_id,
            title=title,
            company=company,
            employment_type=employment_type,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            description=description,
        )
        self.db.add(experience)
        self.db.flush()
        return experience

    def update(
        self,
        experience: Experience,
        *,
        title: str,
        company: str,
        employment_type: EmploymentType,
        start_date: date,
        end_date: date | None,
        is_current: bool,
        description: str | None,
    ) -> Experience:
        experience.title = title
        experience.company = company
        experience.employment_type = employment_type
        experience.start_date = start_date
        experience.end_date = end_date
        experience.is_current = is_current
        experience.description = description
        self.db.flush()
        return experience

    def delete(self, experience: Experience) -> None:
        self.db.delete(experience)
