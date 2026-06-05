"""Wathiq — Application Configuration
Pydantic Settings loading from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://postgres:***@localhost:5432/wathiq"
    supabase_url: str = "https://yywowhdgwcxulgnglcck.supabase.co"
    supabase_key: str = ""
    supabase_service_role_key: str = ""

    # AI Services
    gemini_api_key: str = ""

    # Hermes
    hermes_base_url: str = "http://localhost:8001"
    hermes_auth_token: str = ""

    # Encryption
    encryption_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://wathiq.onrender.com"

    # Logging
    log_level: str = "INFO"

    # Application
    app_name: str = "Wathiq Compliance Gateway"
    app_version: str = "0.2.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()