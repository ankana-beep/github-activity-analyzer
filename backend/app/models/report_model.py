from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    file_path: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    job_id: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}