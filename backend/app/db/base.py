"""Declarative base shared by every ORM model (added starting Phase 3)."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
