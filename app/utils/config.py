from pydantic_settings import BaseSettings
import os
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "sqlite:///./financial_analytics.db"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Financial Analytics API"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis settings
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # File upload settings
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # ML model settings
    MODEL_CACHE_DIR: str = "./models"
    
    # Monitoring settings
    MONITORING_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create directories if they don't exist
def create_directories():
    Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
    Path(settings.MODEL_CACHE_DIR).mkdir(exist_ok=True)

settings = Settings()
create_directories() 