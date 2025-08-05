from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields from .env file
    )
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/mr_wallet_db"
    
    # Security
    APP_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application
    APP_NAME: str = "Mr Wallet API"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False
    APP_ENV: str = "development"
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()
