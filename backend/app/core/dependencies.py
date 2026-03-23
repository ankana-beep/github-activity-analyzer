from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.core.config import get_settings, Settings
from app.db.database import get_db, get_redis
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.github_repository import GithubRepository
from app.repositories.job_repository import JobRepository
from app.repositories.report_repository import ReportRepository
from app.services.resume_parser_service import ResumeParserService
from app.services.github_service import GithubService
from app.services.activity_analyzer_services import ActivityAnalyzerService
from app.services.ai_summary_service import AISummaryService
from app.services.compatibility_service import CompatibilityService
from app.services.pdf_report_service import PdfReportService


# Repositories

def get_candidate_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> CandidateRepository:
    return CandidateRepository(db)

def get_github_repo(
    db: AsyncIOMotorDatabase = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> GithubRepository:
    return GithubRepository(db, redis)

def get_job_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> JobRepository:
    return JobRepository(db)

def get_report_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)


# Services

def get_resume_parser(settings: Settings = Depends(get_settings)) -> ResumeParserService:
    return ResumeParserService(settings)

def get_github_service(
settings: Settings = Depends(get_settings),
github_repo : GithubRepository = Depends(get_github_repo),
) -> GithubService:
    return GithubService(settings, github_repo)

def get_activity_analyzer() -> ActivityAnalyzerService:
    return ActivityAnalyzerService()

def get_ai_summary(settings: Settings = Depends(get_settings)) ->AISummaryService:
    return AISummaryService(settings)

def get_compatibility_service(
    settings: Settings = Depends(get_settings),
) -> CompatibilityService:
    return CompatibilityService(settings)

def get_pdf_service(settings: Settings = Depends(get_settings)) -> PdfReportService:
    return PdfReportService(settings)