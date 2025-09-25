"""
Application configuration settings with dynamic environment variable support.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database - Will be provided by Render's environment variables
    DATABASE_URL: str = "postgresql://user:password@localhost/automatizaciones"  # Default for local development
    
    # WhatsApp Cloud API - All required for production
    WHATSAPP_TOKEN: os.getenv("WHATSAPP_TOKEN")
    PHONE_NUMBER_ID: os.getenv("PHONE_NUMBER_ID")
    BUSINESS_ID: os.getenv("BUSINESS_ID")
    WEBHOOK_VERIFY_TOKEN: os.getenv("WEBHOOK_VERIFY_TOKEN")
    
    # Security - Must be set in production
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Dynamic frontend URL support
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Local development
        os.getenv("FRONTEND_URL", "https://your-frontend.onrender.com")  # Production
    ]
    
    # Redis - Dynamic Redis URL support
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379")
    
    # Application
    APP_NAME: str = "WhatsApp Automation MVP"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Render Service IDs - For deployment automation
    RENDER_BACKEND_SERVICE_ID: Optional[str] = None
    RENDER_FRONTEND_SERVICE_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()