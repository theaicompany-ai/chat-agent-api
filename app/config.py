# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Dict

class Settings(BaseSettings):
    APP_NAME: str = "The AI Company Agent"
    DEBUG: bool = True  # Set to True for development
    VERSION: str = "1.0.0"
    GROQ_API_KEY: str  # Will be loaded from environment variable
    APP_API_KEY: str  # Will be loaded from environment variable
    OPENAI_SWARM_API_KEY: str  # Will be loaded from environment variable
    SWARM_SETTINGS: Dict[str, int] = {
        "max_concurrent_calls": 5,
        "timeout": 30,
    }
    FRESHDESK_DOMAIN: str
    FRESHDESK_API_KEY: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
