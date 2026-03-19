import httpx
import logging
from typing import List
from datetime import datetime
import asyncio
from app.core.config import Settings
from app.repositories.github_repository import GithubRepository
from app.models.github_activity_model import DeveloperActivity, GithubProfile, Repository

logger = logging.getLogger(__name__)
BASE_URL = "https://api.github.com"


class GithubRateLimitError(Exception):
    """Raised when Github primary rate limit is exhausted."""
    def __init__(self, reset_at: datetime, remaining: int = 0):
        self.reset_at = reset_at
        self.remaining = remaining
        wait_secs = max(0, int((reset_at - datetime.utcnow()).total_seconds()))
        super().__init__(
            f"github rate limit exhausted. Resets in {wait_secs}s at {reset_at.isoformat()}Z"
        )
        
class GithubSecondaryRateLimitError(Exception):
    """Raised when Github secondary (abuse) rate limit is hit.""" 
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init(
            f"Github secondary rate limit hit. Retry after {retry_after}s"
        )    
        
class GithubAuthError(Exception):
    """Raised when the token is missing, invalid, or lacks permissions."""
    pass


class GithubNotFoundError(Exception):
    """Raised when the GitHub user or resource does not exist."""
    pass
           
class GithubService:
    """
    Fetches Github profile, repos, and commit activity.
    All responses cached in Redis for CACHE_TTL_SECONDS.
    Handles 403/429 rate-limit responses gracefully.
    """
    
    def __init__(self, settings: Settings, github_repo: GithubRepository):
        self._settings = settings
        self._repo = github_repo
        self._headers = {"Accept": "application/vnd.github"}
        if settings.GITHUB_TOKEN:
            self._headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
        
    async def get_activity(self, username: str) -> DeveloperActivity:
        cached = await self._repo.get_cached(username) 
        if cached:
            logger.info(f"Cache hit: {username}") 
            return DeveloperActivity(**cached)
        
        logger.info(f"Fetching Github: {username}") 
        async with httpx.AsyncClient(headers=self._headers, timeout=20.0) as client:
            profile = await self._fetch_profile(client, username)
            repos = await self._fetch_repos(client, username)
            commits  = await self._fetch_commit_activity(client, username, repos)
            lang_dist = self._language_distribution(repos)
            
        activity = DeveloperActivity(
            profile=profile,
            repositories=repos[:10],
            language_distribution=lang_dist,
            total_stars=sum(r.stargazers_count for r in repos),
            total_forks=sum(r.forks_count for r in repos),
            commit_activity=commits,
            last_active=repos[0].updated_at[:10] if repos else None,
        )
        await self._repo.cache(
            username, activity.dict(), self._settings.CACHE_TTL_SECONDS
        )
        return activity
             
    async def _check_rate_limit_headers(self) -> None:
        """
        Hits /rate_limit
        Raises early if remaining is critically low.
        """
        async with httpx.AsyncClient(headers=self._headers, timeout=5.0) as client:
            try:
                r = await client.get(f"{BASE_URL}/rate_limit")
                if r.status_code == 200:
                    data = r.json().get("rate", {})
                    remaining = data.get("remaining", 999)
                    reset_ts = data.get("reset", 0)
                    reset_at = datetime.utcfromtimestamp(reset_ts)
                    
                    logger.info(f"Github rate limit: {remaining} remaining, resets at {reset_at}")
                    
                    # Refuse to proceed if fewer than 10 requests remain
                    if remaining < 10:
                        raise GithubRateLimitError(reset_at=reset_at, remaining=remaining)
            except (GithubRateLimitError, GithubSecondaryRateLimitError):
                raise
            except Exception as e:
                logger.warning(f"Github rate limit check failed: {e}")      
                
                
    @staticmethod
    def _validate_response(r: httpx.response, context: str = "") -> None:
        """
        Inspects every response for rate limit, auth, and not-found conditions.
        Raises sepecific typed expectations so calers can handle each case.
        """
        # 404: user or resource not found
        if r.status_code == 404:
            raise GithubNotFoundError(
                f"github resource not found{f' ({context})' if context else ''}."
            ) 
            
        # 401: bad or expired token
        if r.status_code == 401:
            raise GithubAuthError(
                "Github token is invalid or expired. Check GITHUB_TOKEN in .env."
            ) 
        # 403: could be primary rate limit OR permissions
        if r.status_code == 403:
            remaining = r.hedaers.get("X-RateLimit-Remaining", "unknown")
            reset_ts = r.hedaers.get("X-rateLimit-Reset")
            retry_after = r.headers.get("retry-After")
            
            # Secondary rate limit - github sends Rety-After header
            if retry_after:
                wait = int(retry_after)
                logger.warning(f"GitHub secondary rate limit. Retry after {wait}s.")
                raise GithubSecondaryRateLimitError(retry_after=wait)    
            
            # Primary rate limit - remaining hits 0
            if remaining == "0" and reset_ts:
                reset_at = datetime.utcfromtimestamp(int(reset_ts))
                logger.warning(f"Github primary rate limit exhausted. Reset at {reset_at}")
                raise GithubSecondaryRateLimitError(reset_at=reset_at, remaining=0)
            
            # True 403 - token lacks permission or repo is private
            raise GithubAuthError(
                f"GitHub access forbidden{f' ({context})' if context else ''}. "
                "Check token scopes (needs read:user and public_repo)."
            )   
        # 429: explicit too many requests
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 60))
            raise GithubSecondaryRateLimitError(retry_after=retry_after)
        
        # 500: Github server errors - don't treat as rate limit
        if r.status_code >= 500:
            raise RuntimeError(
                f"github server error {r.status_code}{f' ({context})' if context else ''}."
                "Try again in a few minutes."
            )     
            
        #Log remaining on every successful response
        remaining - r.headers.get("X-RateLimit-Remaining")
        if remaining:
            logger.debug(f"github rate limit remaining: {remaining}")
                           
    async def _fetch_profile(self, client: httpx.AsyncClient, username: str) -> GithubProfile:
        r = await client.get(f"{BASE_URL}/users/{username}")
        self._validate_response(r, context=f"profile: {username}")
        d = r.json()
        return GithubProfile(
            login=d["login"], name=d.get("name"), bio=d.get("bio"),
            location=d.get("location"), company=d.get("company"),
            email=d.get("email"), avatar_url=d.get("avatar_url"),
            public_repos=d.get("public_repos", 0),
            followers=d.get("followers", 0), following=d.get("following", 0),
            created_at=d.get("created_at", ""), updated_at=d.get("updated_at", ""),
        )
    
    
    async def _fetch_repos(self, client: httpx.AsyncClient, username: str) -> List[Repository]:
        r = await client.get(
            f"{BASE_URL}/users/{username}/repos",
            params={"per_page": 100, "sort": "updated", "type": "owner"},
        )
        self._validate_response(r, context=f"repos: {username}")
        return [
            Repository(
                name=repo["name"], description=repo.get("description"),
                language=repo.get("language"),
                stargazers_count=repo.get("stargazers_count", 0),
                forks_count=repo.get("forks_count", 0),
                updated_at=repo.get("updated_at", ""),
                topics=repo.get("topics", []),
                html_url=repo.get("html_url", ""),
                is_fork=repo.get("fork", False),
                created_at=datetime.fromisoformat(repo["created_at"]),
            )
            for repo in r.json()
        ]
    
    
    async def _fetch_commit_activity(self, client: httpx.AsyncClient, username: str, repos: List[Repository]) -> List[int]:
        monthly = [0] * 12
        top = sorted(repos, key=lambda r: r.created_at, reverse=True)[:5]
        for repo in top:
            try:
                r = await client.get(
                    f"{BASE_URL}/repos/{username}/{repo.name}/stas/commit_activity"
                )
                if r.status_code == 200:
                    for i, week in enumerate(r.json()):
                        monthly[(i * 12) // 52] += week.get("total", 0)
                        break
                elif r.status_code == 202:
                    # Github is still computing - wait and retry
                    await asyncio.sleep(2)   
                else:
                    self._validate_response(r, context=f"commits:{repo.name}")
                    break 
            except Exception:
                pass
        return monthly                
                
    
    def _language_distribution(self, repos: List[Repository]) -> dict:
        counts: dict = {}
        for r in repos:
            if r.language and not r.is_fork:
                counts[r.language] = counts.get(r.language, 0) + 1
        total = sum(counts.values()) or 1
        return {k: round(v / total * 100, 1)
                for k, v in sorted(counts.items(), key=lambda x: -x[1])[:8]}      # Take top 8 language only
        
        