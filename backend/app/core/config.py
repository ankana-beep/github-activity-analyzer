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
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    REDIS_URL: str = os.getenv("REDIS_URL")
    CACHE_TTL_SECONDS: int = os.getenv("CACHE_TTL_SECONDS")
    
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    MONGODB_DB: str = os.getenv("MONGODB_DB")
    
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    MAX_FILE_SIZE_MB: int = os.getenv("MAX_FILE_SIZE_MB")
    
    REPORT_OUTPUT_DIR:str = os.getenv("REPORT_OUTPUT_DIR")
    print("REPORT_OUTPUT_DIR", REPORT_OUTPUT_DIR)
    print("MONGODB_DB", MONGODB_DB)
    print("MONGODB_URL", MONGODB_URL)
    print("REDIS_URL", REDIS_URL)
    print("GITHUB_TOKEN", GITHUB_TOKEN)
    print("OPENAI_API_KEY", OPENAI_API_KEY)
    print("MAX_FILE_SIZE_MB", MAX_FILE_SIZE_MB)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()