from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Compatibility schema

class CompatibilitySchema(BaseModel):
    job_id: str
    job_title: str
    score: float
    match_level: str
    skill_match: float
    experience_match: float
    github_relevance: float
    language_match: float
    explanation: str
    matched_skills: List[str]
    missing_skills: List[str]
    
    
class CompatibilityRequest(BaseModel):
    candidate_id: str
    job_id: str    
    