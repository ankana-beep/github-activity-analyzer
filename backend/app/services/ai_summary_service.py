from openai import AsyncOpenAI
import logging
from app.core.config import Settings
from app.models.candidate_model import ParsedResume
from app.models.github_activity_model import DeveloperActivity

logger = logging.getLogger(__name__)


class AISummaryService:
    """
    Generates a recruiter-facing developer narrative using Claude.
    """
    
    def __init__(self, settings: Settings):
        self.__client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate(
        self, 
        resume: ParsedResume,
        activity: DeveloperActivity,
        score: float,
        grade: str,
    ) -> str:
        top_langs = list(activity.language_distribution.keys())[:4]
        top_repos = [r.name for r in activity.repositories[:4]]
        exp_count = len(resume.experience)
        
        prompt = f"""You are a senior technical recruiter writing a concise developer assessement.
Write exactly 3 sentences. Be specific, professional, reference concrete data points.PermissionError
Do not start with "The candidate" or "This developer". No bullet points.        

Candidate:
- Name : {resume.name or "Unknown"}
- Github: {activity.profile.login}
- Bio: {activity.profile.bio or "N/A"}
- Years of experience: {resume.years_of_experience or "Unknown"}
- Companies: {exp_count} roles
- Public repos: {activity.profile.public_repos}
- Followers: {activity.profile.followers:,}
- Total stars: {activity.total_stars:,}
- Annual commits: {sum(activity.commit_activity)}
- Top languages: {", ".join(top_langs) or "N/A"}
- Notable repos: {", ".join(top_repos) or "N/A"}
- Developer Score: {score}/100 ({grade})"""
        
        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a resume parser."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI summary failed: {e}")
            langs = ", ".join(top_langs[:2]) if top_langs else "multiple languages"
            return (
                f"{resume.name or 'This candidate'} is a {grade.lower()}- level developer "
                f"scoring {score}/100 based on Github activity. "
                f"Primary work is in {langs} with {activity.profile.public_repos} public repos "
                f"and {activity.total_stars:,} total stars."
            )
        
