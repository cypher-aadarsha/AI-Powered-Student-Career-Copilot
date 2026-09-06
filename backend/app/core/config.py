"""Application settings, sourced entirely from environment variables.

Never hardcode secrets here. `.env` (gitignored) supplies local values;
`.env.example` documents every key a new environment must set.
"""
from functools import lru_cache

from pydantic import Field, field_validator
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
    llm_api_base_url: str | None = None
    llm_model: str = Field(default="gpt-4o-mini", description="Chat-completions model name for the 'llm' provider.")

    # --- Resume storage (Phase 5) ---
    resume_storage_dir: str = Field(default="storage/resumes", description="Path is relative to the backend/ dir.")
    resume_max_size_mb: int = Field(default=5)

    @field_validator("llm_api_key", "llm_api_base_url", mode="before")
    @classmethod
    def _blank_env_value_means_unset(cls, value: str | None) -> str | None:
        # An .env line like `LLM_API_KEY=` sets the env var to "", which is
        # a present-but-empty override — treat it the same as unset.
        return value or None


@lru_cache
def get_settings() -> Settings:
    return Settings()
