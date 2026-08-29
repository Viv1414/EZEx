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
    # real secret via an env var, never commit one to the repo. The check
    # below makes forgetting that a startup crash instead of a silent hole.
    secret_key: str = "dev-only-insecure-secret-change-me"
    access_token_expire_minutes: int = 60 * 24  # 1 day -- with revocation-on-logout, no refresh-token flow needed

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


INSECURE_DEFAULT_SECRET_KEY = "dev-only-insecure-secret-change-me"

# Import this single instance everywhere instead of instantiating Settings()
# again -- keeps config reads consistent and lets us swap the source
# (env vars, secrets manager, etc.) in one place later.
settings = Settings()

if settings.environment == "production" and settings.secret_key == INSECURE_DEFAULT_SECRET_KEY:
    # Refuse to even start rather than run in production with a JWT secret
    # anyone who's read this file could use to forge a login for any user.
    raise RuntimeError(
        "SECRET_KEY is still the insecure dev default. Set a real SECRET_KEY "
        "env var before running with ENVIRONMENT=production."
    )
