from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class GithubProfile(BaseModel):
    login: str
    name: Optional[str] =  None
    bio: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 
    
    
class Repository(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow) 
    topics: List[str] = []
    html_url: str = ""
    is_fork: bool = False
    
class DeveloperActivity(BaseModel):
    profile: GithubProfile
    repositories: List[Repository] = []
    language_distribution: Dict[str, float] = {}
    total_stars: int = 0
    total_forks: int = 0
    commit_activity: List[int] = []  # 12 monthly buckets
    last_active: Optional[str] = None
    top_languages: List[str] = []
            