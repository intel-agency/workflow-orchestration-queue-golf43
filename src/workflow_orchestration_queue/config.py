"""
Application settings using pydantic-settings.

Loads configuration from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # GitHub Configuration
    github_token: str = ""
    github_repo: str = "intel-agency/workflow-orchestration-queue-golf43"
    github_owner: str = "intel-agency"
    sentinel_bot_login: str = ""
    webhook_secret: str = ""

    # Sentinel Configuration
    poll_interval: int = 60
    max_backoff: int = 960
    heartbeat_interval: int = 300
    daily_budget_limit: float = 10.00

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
