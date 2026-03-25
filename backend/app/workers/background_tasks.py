import logging
from datetime import datetime

from app.repositories.candidate_repository import CandidateRepository
from app.services.resume_parser_service import ResumeParserService
from app.services.github_service import GithubService
from app.services.activity_analyzer_services import ActivityAnalyzerService
from app.services.ai_summary_service import AISummaryService

logger = logging.getLogger(__name__)

async def process_candidate_pipeline(
    candidate_id: str,
    file_bytes: bytes,
    filename: str,
    candidate_repo: CandidateRepository,
    resume_parser: ResumeParserService,
    github_service: GithubService,
    activity_analyzer: ActivityAnalyzerService,
    ai_summary: AISummaryService
    ) ->None:
    """
    Full analysis pipeline:
      1. Parse resume (AI extraction)
      2. Resolve GitHub username
      3. Fetch GitHub activity (Redis-cached)
      4. Compute developer score
      5. Generate AI insight
      6. Persist to MongoDB
    """
    logger.info(f"[Pipeline] starting for {candidate_id}")
    try:
      # Starge 1: Parse resume
      await candidate_repo.update(candidate_id, {"status": "parsing_resume"})
      parsed = await resume_parser.parse(file_bytes, filename)
      await candidate_repo.update(candidate_id, {
        "parsed_resume": parsed.dict(),
        "status": "fetching_github",
      })
      logger.info(f"[Pipeline] Resume parsed . github={parsed.github_username}")
      if not parsed.github_username:
        raise ValueError("No Github username found in resume.")
      
      # Stage 2: Github activity
      activity = await github_service.get_activity(parsed.github_username)
      logger.info(f"[Pipeline] Github fetched for {parsed.github_username}")
      
      # Stage 3: Developer score 
      await candidate_repo.update(candidate_id, {"status": "analyzing"})
      score = activity_analyzer.compute_score(activity)
      grade = activity_analyzer.grade(score)
      
      # Stage 4: AI insight
      await candidate_repo.update(candidate_id, {"status":"generating_insight"})
      insight = await ai_summary.generate(parsed, activity, score, grade)
      
      # Stage 5: Persist
      await candidate_repo.update(candidate_id, {
        "github_data": activity.dict(),
        "developer_score": score,
        "score_grade": grade,
        "ai_insight": insight,
        "status": "complete",
        "updated_at": datetime.utcnow(),
      })
      logger.info(f"[Pipeline] Complete . candidate={candidate_id} . score={score}")
      
    except ValueError as e:
      logger.warning(f"[Pipeline] Validation error . {candidate_id}: {e}")
      await candidate_repo.update(candidate_id, {
        "status": "error",
        "error_message": "An unexpected error occured during processing.",
      })   