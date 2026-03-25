from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Resume Upload Schema

class ResumeUploadResponse(BaseModel):
    candidate_id: str
    status: str
    message: str
    
    