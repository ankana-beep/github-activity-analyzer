import logging
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import (
    get_job_repo, get_candidate_repo,
    get_github_service, get_compatibility_service,
    get_activity_analyzer,
)
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_repository import CandidateRepository
from app.services.github_service import GithubService
from app.services.activity_analyzer_services import ActivityAnalyzerService
from app.services.compatibility_service import CompatibilityService
from app.models.job_model import Job
from app.schemas.job_schema import JobCreateRequest, JobResponse
from app.schemas.compatibility_schema import CompatibilityRequest, CompatibilitySchema
from app.models.github_activity_model import DeveloperActivity
    

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    payload: JobCreateRequest,
    job_repo: JobRepository = Depends(get_job_repo),
):
    """Create a job posting."""
    job = Job(**payload.dict())
    await job_repo.create(job)
    return job

@router.get("/", response_model=list[JobResponse])
async def list_jobs(job_repo: JobRepository = Depends(get_job_repo)):
    jobs = await job_repo.list_all()
    return jobs

@router.get("/{job_id}", reponse_model=JobResponse)
async def get_job(job_id: str, job_repo: JobRepository = Depends(get_job_repo)):
    job = await job_repo.find_by_id(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return JobResponse(**job.dict(), created_at=job.created_at.isoformat())

@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str, job_repo: JobRepository = Depends(get_job_repo)):
    await job_repo.delete(job_id)
    
@router.post("/compatibility", response_model=CompatibilitySchema)
async def compute_compatibility(
    payload: CompatibilityRequest,
    candidate_repo: CandidateRepository = Depends(get_candidate_repo),
    job_repo: JobRepository = Depends(get_job_repo), 
    github_service: GithubService = Depends(get_github_service),
    compatibility_service: CompatibilityService = Depends(get_compatibility_service),
    analyzer: ActivityAnalyzerService = Depends(get_activity_analyzer),
):
    """
    Compute compatibility score between a candidate and a job.
    Stores result in candidate.compatibility_scores[job_id].
    """
    candidate = await candidate_repo.find_by_id(payload.candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found.")
    if candidate.status != "complete":
        raise HTTPException(400, "Candidate analysis not yet complete.")
    
    job = await job_repo.find_by_id(payload.job_id)
    if not job:
        raise HTTPException(404, "Job not found.")

    if not candidate.github_data:
        raise HTTPException(400, "No Github data for this candidate.")
    activity = DeveloperActivity(**candidate.github_data)    
    
    result = await compatibility_service.compute(candidate.parsed_resume, activity, job)
    scores = candidate.compatibility_scores or {}
    await candidate_repo.update(payload.candidate_id, {"compatibility_scores": scores})
    return CompatibilitySchema(*result.dict())