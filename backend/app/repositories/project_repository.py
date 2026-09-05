import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectSkill


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_profile(self, student_profile_id: uuid.UUID) -> list[Project]:
        stmt = select(Project).where(Project.student_profile_id == student_profile_id).order_by(Project.created_at.desc())
        return list(self.db.scalars(stmt))

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return self.db.get(Project, project_id)

    def create(
        self,
        *,
        student_profile_id: uuid.UUID,
        title: str,
        description: str | None,
        repo_url: str | None,
        demo_url: str | None,
        start_date: date | None,
        end_date: date | None,
        skill_ids: list[uuid.UUID],
    ) -> Project:
        project = Project(
            student_profile_id=student_profile_id,
            title=title,
            description=description,
            repo_url=repo_url,
            demo_url=demo_url,
            start_date=start_date,
            end_date=end_date,
        )
        self.db.add(project)
        self.db.flush()
        self._set_skills(project, skill_ids)
        return project

    def update(
        self,
        project: Project,
        *,
        title: str,
        description: str | None,
        repo_url: str | None,
        demo_url: str | None,
        start_date: date | None,
        end_date: date | None,
        skill_ids: list[uuid.UUID],
    ) -> Project:
        project.title = title
        project.description = description
        project.repo_url = repo_url
        project.demo_url = demo_url
        project.start_date = start_date
        project.end_date = end_date
        self._set_skills(project, skill_ids)
        self.db.flush()
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)

    def _set_skills(self, project: Project, skill_ids: list[uuid.UUID]) -> None:
        for existing in list(project.skills):
            self.db.delete(existing)
        self.db.flush()
        for skill_id in dict.fromkeys(skill_ids):  # de-dupe, preserve order
            self.db.add(ProjectSkill(project_id=project.id, skill_id=skill_id))
