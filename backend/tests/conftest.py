"""Shared fixtures. Auth/RBAC tests run against a disposable in-memory
SQLite database rather than requiring a live Postgres — the models use
dialect-generic SQLAlchemy types (Uuid, Enum) specifically so this works
(TDD §20: AI/DB tests must not depend on infrastructure that may not be
running in CI or on a contributor's machine).
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers models on Base.metadata
from app.core.rate_limit import reset_all as reset_rate_limits
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    # The rate limiter's counters are module-level, in-memory state shared
    # across the whole pytest process — without resetting them, the many
    # auth requests other test files make would eventually trip the auth
    # rate limit and fail unrelated tests. See test_security_hardening.py
    # for the tests that actually exercise the limiter's own behavior.
    reset_rate_limits()
    yield


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    # SQLite ignores FOREIGN KEY constraints (including ON DELETE
    # RESTRICT/CASCADE/SET NULL) unless explicitly told to enforce them per
    # connection — unlike Postgres, which always enforces them. Without this,
    # tests would silently pass through deletes a real database would reject.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session):
    from fastapi.testclient import TestClient

    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
