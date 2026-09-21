"""
Centralized application settings, loaded from environment variables / .env.
Every other module reads configuration through this object instead of
touching os.environ directly.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me"

    # Database
    database_url: str = "postgresql+asyncpg://codesentinel:codesentinel@localhost:5432/codesentinel"
    sync_database_url: str = "postgresql+psycopg2://codesentinel:codesentinel@localhost:5432/codesentinel"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # GitHub App
    github_app_id: str = ""
    github_app_private_key_path: str = ""
    github_webhook_secret: str = "change-me-webhook-secret"
    github_api_base_url: str = "https://api.github.com"

    # LLM / RAG — fully local via Ollama, no hosted API keys required.
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:3b"
    # Optional larger local model for the Security and Critic agents, where
    # accuracy matters more than speed. Leave blank to use llm_model for everything.
    llm_model_heavy: str = ""
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768  # nomic-embed-text output size; change if you swap embedding models

    # Risk scoring
    risk_high_threshold: int = 75
    risk_medium_threshold: int = 40

    # Analyzer timeouts (seconds)
    analyzer_timeout: int = 60

    # Max files/diff size the pipeline will process in one run
    max_changed_files: int = 60
    max_diff_bytes_per_file: int = 200_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
