from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.experience_education_schema import ExperienceSchema, EducationSchema

class ParsedResumeSchema(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    github_url: Optional[str]
    github_username: Optional[str]
    linkedin: Optional[str]
    skills: List[str] = None
    experience: List[ExperienceSchema]
    education: List[EducationSchema]
    summary: Optional[str]
    years_of_experience: Optional[float]
    