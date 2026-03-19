from fastapi import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Github schema

class GithubProfileSchema(BaseModel):
    login: str
    name: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    company: Optional[str]
    avatar_url: Optional[str]
    public_repos: int
    followers: int
    following: int
    
class RepositorySchema(BaseModel):
    name: str
    description: Optional[str]
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    html_url: str
    topics: List[str]
    created_at: datetime
    
class GithubActivitySchema(BaseModel):
    profile: GithubProfileSchema
    repositories: List[RepositorySchema]
    language_distribution: Dict[str, float]
    total_stars: int
    total_forks: int
    commit_activity: List[int]
    last_active: Optional[str]
    top_languages: List[str]                   