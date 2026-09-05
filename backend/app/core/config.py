"""Application settings, sourced entirely from environment variables.

Never hardcode secrets here. `.env` (gitignored) supplies local values;
`.env.example` documents every key a new environment must set.
"""
from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "Career Copilot API"
    environment: str = Field(default="development")  # development | test | production
    debug: bool = Field(default=True)

    # --- Database ---
    database_url: str = Field(
        default="postgresql+psycopg2://copilot:copilot@localhost:5432/career_copilot",
        description="SQLAlchemy connection string for PostgreSQL.",
    )

    # --- Auth (used starting Phase 3) ---
    jwt_secret_key: str = Field(default="change-me-in-env", description="Never use the default outside local dev.")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- CORS ---
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- AI provider (wired starting Phase 5) ---
    ai_provider: str = Field(default="mock", description="'mock' or 'llm' — see ai/provider.py")
    llm_api_key: str | None = None
    llm_api_base_url: AnyHttpUrl | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
