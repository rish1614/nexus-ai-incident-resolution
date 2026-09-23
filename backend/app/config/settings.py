"""
Central application configuration.

All configuration is loaded from environment variables (see .env.example).
No secrets are hardcoded. Settings are typed and validated via Pydantic.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    app_env: str = "development"
    app_name: str = "nexus"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # --- Database ---
    database_url: str = "postgresql+asyncpg://nexus:nexus_dev_password@localhost:5432/nexus"
    postgres_user: str = "nexus"
    postgres_password: str = "nexus_dev_password"
    postgres_db: str = "nexus"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379

    # --- Auth ---
    jwt_secret_key: str = "change_me_in_local_env_only"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    # --- LLM / Embedding providers (abstracted; used starting Phase 5) ---
    llm_provider: str = "anthropic"
    llm_api_key: str = ""
    llm_model_name: str = ""
    embedding_provider: str = "anthropic"
    embedding_api_key: str = ""
    embedding_model_name: str = ""

    # --- Observability ---
    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "nexus-backend"

    # --- CORS ---
    cors_allow_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — avoids re-parsing env on every call."""
    return Settings()
