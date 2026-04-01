import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    
    APP_NAME: str = "Recruiter Intelligence Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5174", "http://localhost:3000", "https://github-activity-analyzer.vercel.app", "https://github-activity-analyzer.vercel.app/"]
    
    REDIS_URL: str = os.getenv("REDIS_URL")
    CACHE_TTL_SECONDS: int = os.getenv("CACHE_TTL_SECONDS")
    
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "recruiter_platform")
    
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    MAX_FILE_SIZE_MB: int = os.getenv("MAX_FILE_SIZE_MB")
    
    REPORT_OUTPUT_DIR:str = os.getenv("REPORT_OUTPUT_DIR")
 
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()