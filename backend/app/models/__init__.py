"""Import every model module here so Base.metadata sees all tables —
Alembic's env.py and the test fixtures both rely on this side effect.
"""
from app.models.user import User, UserRole  # noqa: F401
