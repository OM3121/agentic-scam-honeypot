from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_key: str = "default-api-key-change-me"
    api_key_header: str = "X-API-Key"
    
    # Application
    app_title: str = "Agentic Scam Honeypot API"
    app_version: str = "0.1.0"
    app_description: str = "Backend REST API for scam detection and intelligence gathering"
    
    # Session Management
    max_messages_per_session: int = 20
    session_timeout_seconds: int = 3600  # 1 hour
    min_messages_for_callback: int = 3  # Minimum messages before callback is sent
    
    # Scam Detection
    scam_confidence_threshold: float = 0.6
    
    # Callback Configuration
    # Note: Callback URL is hardcoded to hackathon endpoint in callback_service.py
    callback_url: Optional[str] = None  # Deprecated - using hardcoded hackathon URL
    callback_timeout: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
