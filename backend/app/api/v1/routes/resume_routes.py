import logging
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException

from app.core.config import get_settings, Settings
from app.core.dependencies import (
    get_candidate_repo, get_resume_parser, get_github_service,
    get_activity_analyzer, get_ai_summary,
)
from app.repositories.candidate_repository import CandidateRepository
from app.services.resume_parser_service import ResumeParserService
from app.services.github_service import GithubService
from app.services.activity_analyzer_services import ActivityAnalyzerService
from app.services.ai_summary_service import AISummaryService
from app.models.candidate_model import Candidate
from app.schemas.resume_upload_schema import ResumeUploadResponse
from app.schemas.report_schema import ReportResponse
from app.models.github_activity_model import DeveloperActivity
from app.utils.file_utils import validate_resume_file, check_file_size
from app.workers.background_tasks import process_candidate_pipeline

logger=logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["Resume"])

PROCESSING_STATUSES = {
    "pending", "parsing_resume", "fetching_github",
    "analyzing", "generating_insight"
}

@router.post("/upload", response_model=ResumeUploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    candidate_repo: CandidateRepository  = Depends(get_candidate_repo),
    resume_parser: ResumeParserService = Depends(get_resume_parser),
    github_service: GithubService = Depends(get_github_service),
    activity_analyzer: ActivityAnalyzerService = Depends(get_activity_analyzer),
    ai_summary: AISummaryService = Depends(get_ai_summary),
):
    """Upload a PDF or DOCX resume. Returns candidate_id for polling."""
    validate_resume_file(file, max_size_mb=settings.MAX_FILE_SIZE_MB)
    content = await file.read()
    check_file_size(content, max_size_mb=settings.MAX_FILE_SIZE_MB)
    
    candidate = Candidate(raw_filename=file.filename or "resume")
    await candidate_repo.create(candidate)
    logger.info(f"Candidate created: {candidate.id}")
    
    background_tasks.add_task(
        process_candidate_pipeline,
        candidate.id, content, file.filename or "resume",
        candidate_repo, resume_parser, github_service,
        activity_analyzer, ai_summary,
    )
    
    return ResumeUploadResponse(
        candidate_id=candidate.id,
        status="processing",
        message="Resume received. Poll GET /resume/{id}/report for results"
    )
    
@router.get("/{candidate_id}/report", response_model=ReportResponse)
async def get_report(
    candidate_id: str,
    candidate_repo: CandidateRepository = Depends(get_candidate_repo),
):
    """Poll for analysis report. Returns HTTP 202 while processings."""
    candidate = await candidate_repo.find_by_id(candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found.")
    if candidate.status in PROCESSING_STATUSES:
        raise HTTPException(202, f"Still processing: {candidate.status}")
    
    git_activity = None
    if candidate.github_data:
        activity = DeveloperActivity(**candidate.github_data)
        git_activity = {
            "profile": activity.profile.dict(),
            "repositories": [r.dict() for r in activity.repositories],
            "language_distribution": activity.language_distribution,
            "total_stars": activity.total_stars,
            "total_forks": activity.total_forks,
            "commit_activity": activity.commit_activity,
            "last_active": activity.last_active,
            "top_languages": activity.top_languages
        }
    return ReportResponse(
        candidate_id=candidate.id,
        status=candidate.status,
        parsed_resume=candidate.parsed_resume.dict() if candidate.parsed_resume else None,
        github_activity=git_activity,
        developer_score=candidate.developer_score,
        score_grade=candidate.score_grade,
        ai_insight=candidate.ai_insight,
        compatibility_scores=candidate.compatibility_scores,
        error_message=candidate.error_message,
        created_at=candidate.created_at.isoformat(),
    )
    