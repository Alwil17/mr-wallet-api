from pydantic_settings import BaseSettings
from pydantic import ConfigDict, computed_field
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields from .env file
    )

    # Database individual fields
    DB_ENGINE: str = "postgresql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "mr_wallet_db"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Security
    APP_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    APP_NAME: str = "Mr Wallet API"
    APP_VERSION: str = "1.0.1"
    APP_DEBUG: bool = False
    APP_ENV: str = "production"

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()
