"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://kracc:kracc@db:5432/kracc"
    database_url_sync: str = "postgresql://kracc:kracc@db:5432/kracc"
    age_graph_name: str = "kr_acc"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"

    # External APIs
    assembly_api_key: str = ""
    dart_api_key: str = ""

    # Labeling tool
    labeling_invite_code: str = "cookiedeal2026"
    labeling_jwt_secret: str = "change-me-in-production-kr-acc-labeling"
    labeling_jwt_expire_hours: int = 24

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
