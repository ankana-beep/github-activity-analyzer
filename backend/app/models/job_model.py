from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: Optional[str] = None
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        

class CompatibilityResult(BaseModel):
    job_id: str
    job_title: str
    score: float                 # 0-100
    match_level: str             # Excellent / Good / Moderate / Poor
    skill_match: float
    experience_match: float
    github_relevance: float
    language_match: float
    explanation: str
    matched_skills: List[str] = []
    missing_skills: List[str] = []