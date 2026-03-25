import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_github_service, get_activity_analyzer
from app.services.github_service import GithubService
from app.services.activity_analyzer_services import ActivityAnalyzerService

router = APIRouter(prefix="/github", tags=["Github"])


@router.get("/{username}")
async def get_github_profile(
    username: str,
    github_service: GithubService = Depends(get_github_service),
    analyzer: ActivityAnalyzerService = Depends(get_activity_analyzer),
):
    """Fetch Github activity + developer score for any username."""
    try:
        activity = await github_service.get_activity(username)
        score = analyzer.compute_score(activity)
        return {
            "activity": activity.dict(),
            "developer_score": score,
            "score_grade": analyzer.grade(score),
            "breakdown": analyzer.breakdown(activity),
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(404, f"Github user '{username}'not found.") 
        if e.response.status_code in (403, 429):
            raise HTTPException(429, "Github API rate limit reached.")
        raise HTTPException(502, f"Github API error: {e.response.status_code}")
    except RuntimeError as e:
        raise HTTPException(429, str(e))
    
    
@router.delete("/{username}/cache", status_code=204)
async def invalidate_cache(
    username: str,
    github_service: GithubService = Depends(get_github_service),
):
    """Invalidate Redis + Mongo cache for a Github username."""
    await github_service._repo.invalidate(username)