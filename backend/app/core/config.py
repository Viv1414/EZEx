"""
Central app configuration.

All settings are read from environment variables (with defaults for local dev).
In Docker Compose, these get set via the `environment:` block or an `.env` file.
In production, these get set by whatever hosting platform you land on
(env vars set in the platform's dashboard/CLI) -- the code never changes,
only the values do.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    environment: str = "development"  # "development" | "production"

    # Database
    database_url: str = "postgresql+psycopg2://ezpt:ezpt@localhost:5432/ezpt"

    # CORS -- comma-separated list of allowed frontend origins
    cors_origins: str = "http://localhost:3000"

    # Auth -- signs JWTs, so anyone with this value could forge a login.
    # The default here is fine for local dev only; production MUST set a
    # real secret via an env var, never commit one to the repo.
    secret_key: str = "dev-only-insecure-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week -- no refresh-token flow yet

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Import this single instance everywhere instead of instantiating Settings()
# again -- keeps config reads consistent and lets us swap the source
# (env vars, secrets manager, etc.) in one place later.
settings = Settings()
