"""
Service configuration via Pydantic Settings.

How this works:
  1. Pydantic reads each field from environment variables automatically.
  2. If not found in environment, it falls back to the default value.
  3. If a field has no default and is missing from environment, the app crashes
     at startup with a clear error message. This is better than a confusing
     error later when the missing config is first used.

Why not use os.getenv() directly in resolvers or services?
  - It scatters configuration across the codebase.
  - You can't see all config in one place.
  - Testing becomes harder because you can't inject different config.

With this pattern: import settings here, all config is visible in one file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/github_service"
    github_token: str = ""
    app_env: str = "development"
    debug: bool = True

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


# One instance for the whole service. Import this, not Settings.
settings = Settings()
