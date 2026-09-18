from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CodeSentinel"

    database_url: str = (
        "postgresql+psycopg://codesentinel:"
        "codesentinel@localhost:5432/codesentinel"
    )

    redis_url: str = "redis://localhost:6379/0"

    github_token: str = ""

    class Config:
        env_file = ".env"


settings = Settings()