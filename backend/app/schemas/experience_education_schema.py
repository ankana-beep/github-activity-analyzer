from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Experience/Education Schema

class ExperienceSchema(BaseModel):
    company: Optional[str]
    role: Optional[str]
    duration: Optional[str]
    description: Optional[str]
    
class EducationSchema(BaseModel):
    institution: Optional[str]
    degree: Optional[str]    
    year: Optional[str]
    
    