from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Two database URLs because FastAPI and Celery need different drivers.
    # The database itself is the same — only the Python driver changes.
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5434/resume_service"
    celery_database_url: str = "postgresql+psycopg2://postgres:password@localhost:5434/resume_service"

    redis_url: str = "redis://localhost:6379/0"
    app_env: str = "development"
    debug: bool = True


settings = Settings()
