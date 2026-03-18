from fastapi import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Job schema

class JobCreateRequest(BaseModel):
    title: str
    company: Optional[str] = None
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    location: Optional[str] = None
    
class JobResponse(BaseModel):
    id: str
    title: str
    company: Optional[str]
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float]
    location: Optional[str]
    created_at: datetime
    
    