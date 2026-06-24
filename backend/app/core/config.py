from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI_SIZHENG_PLATFORM"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_sizheng"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "change-me-in-local-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    backend_cors_origins: list[AnyHttpUrl] = Field(default_factory=list)
    file_storage_root: str = "./storage"
    wechat_provider_mode: str = "log"
    face_provider_mode: str = "disabled"


@lru_cache
def get_settings() -> Settings:
    return Settings()
