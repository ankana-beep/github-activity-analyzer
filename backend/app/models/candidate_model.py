from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    year: Optional[str] = None
    
    
class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    

class ParsedResume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    github_url: Optional[str] = None
    github_username: Optional[str] = None
    linkedin: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    summary: Optional[str] = None
    years_of_experience: Optional[float] = None
    
    
class Candidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  
    raw_filename: str
    parsed_resume: ParsedResume = Field(default_factory=ParsedResume)
    github_data: Optional[dict] = None
    developer_score: Optional[float] = None
    score_grade: Optional[str] = None
    ai_insight: Optional[str] = None
    compatibility_scores: Optional[dict] = None    
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}       