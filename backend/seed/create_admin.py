"""Provisions the initial admin account out-of-band — admin accounts are
never created through self-registration (see AuthService.register's
docstring: "admin accounts are provisioned out-of-band"). Reads credentials
from environment variables so a real password never lives in source control
or in this script.

Idempotent: does nothing if a user with that email already exists (even if
it's a student account — this script only creates, it never promotes).

Usage (from backend/, with DATABASE_URL pointed at the target database):
    ADMIN_EMAIL=admin@careercopilot.io ADMIN_PASSWORD=... python -m seed.create_admin
"""
import os

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository

# Not .local/.test/.example — those are IANA special-use TLDs that EmailStr
# (via email-validator) rejects outright, which would make the seeded
# account unable to log in through the app's own /auth/login (its
# LoginRequest schema validates the email the same strict way).
DEFAULT_ADMIN_EMAIL = "admin@careercopilot.io"


def create_admin(db: Session, *, email: str, password: str, full_name: str) -> bool:
    """Returns True if a new admin account was created, False if an account
    with that email already existed. Flushes but does not commit."""
    users = UserRepository(db)
    if users.get_by_email(email) is not None:
        return False
    users.create(email=email, password_hash=hash_password(password), full_name=full_name, role=UserRole.admin)
    db.flush()
    return True


def run() -> None:
    email = os.environ.get("ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)
    password = os.environ.get("ADMIN_PASSWORD")
    full_name = os.environ.get("ADMIN_FULL_NAME", "Platform Admin")
    if not password:
        raise SystemExit("Set ADMIN_PASSWORD before running this script, e.g.:\n  ADMIN_PASSWORD=... python -m seed.create_admin")

    db = SessionLocal()
    try:
        created = create_admin(db, email=email, password=password, full_name=full_name)
        db.commit()
        print(f"Admin account {'created' if created else 'already existed'}: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
