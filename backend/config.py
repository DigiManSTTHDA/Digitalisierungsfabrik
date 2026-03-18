"""Application configuration via pydantic-settings.

All parameters are loaded from environment variables or a .env file.
See .env.example for the full list with descriptions.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: Literal["anthropic", "openai", "ollama"] = "anthropic"
    llm_model: str = "claude-opus-4-6"
    llm_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Persistence
    database_path: str = "./data/digitalisierungsfabrik.db"

    # Dialog history
    dialog_history_n: int = Field(default=3, ge=1)
    dialog_history_moderator_m: int = Field(default=10, ge=1)

    # Token limits
    token_warn_threshold: int = Field(default=80_000, ge=1)
    token_hard_limit: int = Field(default=100_000, ge=1)

    # Automation
    automation_warn_threshold: int = Field(default=1, ge=0)

    # Logging
    log_level: str = "INFO"
    llm_log_enabled: bool = True
    log_file: str | None = None  # Optional file path for structured log output (LOG_FILE env var)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings — parsed once from .env on first call."""
    return Settings()
