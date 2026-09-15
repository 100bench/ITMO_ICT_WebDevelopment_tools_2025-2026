"""Файл хранит настройки приложения, которые читаются из переменных окружения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Time Manager API"
    database_url: str = "postgresql+psycopg://time_manager:time_manager@localhost:5432/time_manager"
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 120
    parser_owner_email: str = "demo@example.com"
    parser_service_url: str = "http://localhost:8001"
    parser_service_token: str = "change-me-parser-token"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
