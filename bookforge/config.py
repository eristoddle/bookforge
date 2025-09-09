from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Debug and logging
    debug: bool = True
    log_level: str = "INFO"
    
    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # File storage
    temp_dir: str = "./temp_books"
    output_dir: str = "./generated_epubs"
    max_file_size: str = "50MB"
    
    # GitHub integration
    github_token: Optional[str] = None
    
    # EPUB generation
    default_theme: str = "modern"
    epub_validation: bool = True
    
    # API configuration
    max_concurrent_jobs: int = 10
    job_timeout: int = 300
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()


# Create directories if they don't exist
settings = get_settings()
os.makedirs(settings.temp_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)