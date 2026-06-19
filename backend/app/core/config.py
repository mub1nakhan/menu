"""
Core configuration for Restaurant OS API
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Restaurant OS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/restaurant_os"
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str = "your-jwt-secret-key-change-in-production"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    
    # Payment Gateway (Stripe)
    STRIPE_SECRET_KEY: str = "sk_test_your_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_your_key"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif"}
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # AI/ML
    ENABLE_ML_FEATURES: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Constants for access token expiration
ACCESS_TOKEN_EXPIRE_TIMEDELTA = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_TIMEDELTA = timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS)

