"""FastAPI app factory: middleware, exception handlers, router registration.

Routers stay thin and delegate to services (added starting Phase 3) — see
TDD §10 for the full intended module layout.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin, auth, health, profile, users
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

settings = get_settings()
configure_logging("DEBUG" if settings.debug else "INFO")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-Powered Student Career Copilot — REST API. See /docs for the full contract.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root() -> dict:
    return {"data": {"service": settings.app_name, "docs": "/docs"}}
