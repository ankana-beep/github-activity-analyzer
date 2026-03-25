from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.parsed_resume import ParsedResumeSchema
from app.schemas.github_schema import GithubActivitySchema
from app.schemas.compatibility_schema import CompatibilitySchema

# Report schema

class ReportResponse(BaseModel):
    candidate_id: str
    status: str
    parsed_resume: Optional[ParsedResumeSchema]
    github_activity: Optional[GithubActivitySchema]
    developer_score: Optional[float]
    score_grade: Optional[str]
    ai_insight: Optional[str]
    compatibility_scores: Optional[Dict[str, CompatibilitySchema]]
    error_message: Optional[str]
    created_at: datetime