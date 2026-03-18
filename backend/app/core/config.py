from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    
    APP_NAME: str = "Recruiter Intelligence Platform"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "recruiter_intelligence_platform"
    
    REDIS_URL: str = "redis//localhost:6379"
    CACHE_TTL_SECONDS: int = 86400
    
    GITHUB_TOKEN: str =""
    OPENAI_API_KEY: str = ""
    
    MAX_FILE_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()