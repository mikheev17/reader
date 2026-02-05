from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    # Application settings
    APP_NAME: Optional[str] = None
    APP_DESCRIPTION: Optional[str] = None
    DEBUG: Optional[bool] = None
    API_VERSION: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    # JWT settings (set via env)
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = None
    JWT_EXPIRE_MINUTES: Optional[int] = None

    # Cookie auth (name of the cookie holding the Bearer token)
    COOKIE_NAME: str = "access_token"

    # RabbitMQ settings (set via env)
    RM_HOST: Optional[str] = None
    RM_PORT: Optional[int] = None
    RM_USER: Optional[str] = None
    RM_PASS: Optional[str] = None
    RM_VHOST: Optional[str] = None
    ML_QUEUE: Optional[str] = None

    @property
    def DATABASE_URL_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property
    def DATABASE_URL_psycopg(self):
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    # Resolve .env located in the app/ directory regardless of current working dir
    _ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    def validate(self) -> None:
        """Validate critical configuration settings"""
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASS, self.DB_NAME]):
            raise ValueError("Missing required database configuration")
        if not all([self.JWT_SECRET, self.JWT_ALGORITHM, self.JWT_EXPIRE_MINUTES is not None]):
            raise ValueError("Missing required JWT configuration (JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES)")
        if not all([self.RM_HOST, self.RM_PORT is not None, self.RM_USER, self.RM_PASS, self.RM_VHOST, self.ML_QUEUE]):
            raise ValueError("Missing required RabbitMQ configuration (RM_HOST, RM_PORT, RM_USER, RM_PASS, RM_VHOST, ML_QUEUE)")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings
