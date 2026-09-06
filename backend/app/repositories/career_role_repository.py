import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.career_role import CareerRole


class CareerRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[CareerRole]:
        stmt = select(CareerRole).order_by(CareerRole.title)
        return list(self.db.scalars(stmt))

    def get_by_id(self, role_id: uuid.UUID) -> CareerRole | None:
        return self.db.get(CareerRole, role_id)
