import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from app.core.dependencies import (
    get_candidate_repo, get_report_repo,
    get_pdf_service, get_job_repo,
)
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.job_repository import JobRepository
from app.models.job_model import CompatibilityResult
from app.services.pdf_report_service import PdfReportService
from app.models.report_model import Report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/")
async def list_candidates(
    limit: int = Query(default=20, le=100),
    candidate_repo: CandidateRepository = Depends(get_candidate_repo),
):
    """List recent candidate analyses."""
    candidates = await candidate_repo.list_recent(limit=limit)
    return [
        {
            "candidate_id": c.id,
            "name": c.parsed_resume.name,
            "github_username": c.parsed_resume.github_username,
            "developer_score": c.developer_score,
            "score_grade": c.score_grade,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        }
        for c in candidates
    ]
    
@router.get("/{candidate_id}/download") 
async def download_pdf_report(
    candidate_id: str,
    job_id: str | None = Query(default=None),
    candidate_repo: CandidateRepository = Depends(get_candidate_repo),
    report_repo: ReportRepository = Depends(get_report_repo),
    pdf_service: PdfReportService = Depends(get_pdf_service),
):
    """
    Generate and download a PDF report for a candidate.
    Optionally include job compatibility by passing ?job_id=...
    """
    candidate = await candidate_repo.find_by_id(candidate_id)
    if not candidate_id:
        raise HTTPException(404, "Candidate not found.")
    if candidate.status != "complete":
        raise HTTPException(400, "Candidate analysis not complete yet.")
    
    compatibility = None
    if job_id:
        scores = candidate.compatibility_scores or {}
        if job_id in scores:
            compatibility = CompatibilityResult(**scores[job_id])
    
    filepath = await pdf_service.generate(candidate, compatibility)
    if not os.path.exists(filepath):
        raise HTTPException(500, "Report generation failed.")
    
    name = (candidate.parsed_resume.name or "candidate").replace(" ", "_")
    download_name = f"report_{name}.pdf"
    
    report = Report(candidate_id=candidate_id, file_path=filepath, job_id=job_id)
    await report_repo.create(report)
    
    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=download_name,
    )
            