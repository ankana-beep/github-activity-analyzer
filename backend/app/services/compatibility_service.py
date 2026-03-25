import json
import logging
from openai import AsyncOpenAI

from app.core.config import Settings
from app.models.candidate_model import ParsedResume
from app.models.job_model import Job, CompatibilityResult
from app.models.github_activity_model import DeveloperActivity

logger = logging.getLogger(__name__)


class CompatibilityService:
    """
    Computes job compatibility between a candidate and a job description.
    
    Formula:
        Compatibility = (skill_match*0.4) + (experience_match*0.2) + (github_relevance*0.2) + (language_match*0.2)
        
    Uses OpenAI for semantic skill matching and explanation generation    
    """
    
    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def compute(
        self,
        resume: ParsedResume,
        activity: DeveloperActivity,
        job: Job,
    ) -> CompatibilityResult:
        skill_data = self._skill_match(resume.skills, job.required_skills, job.preferred_skills)
        experience_match = self._experience_match(resume.years_of_experience, job.experience_years)
        github_relevance = self._github_relevance(activity, job)
        language_match = self._language_match(activity, job)
        
        score = (
            skill_data["score"] * 0.40 +
            experience_match * 0.20 + 
            github_relevance * 0.20 +
            language_match * 0.20
        )
        score = round(min(score, 100.0), 1)
        match_level = self._match_level(score)
        
        explanation = await self._generate_explanation(
            resume, activity, job, score, skill_data, experience_match
        )
        
        return CompatibilityResult(
            job_id=job.id,
            job_title=job.title,
            score=score,
            match_level=match_level,
            skill_match=round(skill_data["score"], 1),
            experience_match=round(experience_match, 1),
            github_relevance=round(github_relevance, 1),
            language_match=round(language_match, 1),
            explanation=explanation,
            matched_skills=skill_data["matched"],
            missing_skills=skill_data["missing"],
        )
    
    
    def _skill_match(
        self,
        candidate_skills: list,
        required: list,
        preferred: list,
    ) -> dict:
        cset = {s.lower(). strip() for s in candidate_skills}
        rset = {s.lower().strip() for s in required}
        pset = {s.lower().strip() for s in preferred}
        
        matched_req = cset & rset
        match_pref = cset & pset
        missing_req = rset - cset
        
        if not rset:
            score = 100.0
        else:
            req_score = len(matched_req) / len(rset) * 100
            pref_bonus = min(len(match_pref) / max(len(pset), 1) * 20, 20)
            score = min(req_score + pref_bonus, 100.0)
            
        return {
            "score": score,
            "matched":sorted(matched_req | match_pref),
            "missing": sorted(missing_req),
        }        
        
    def _experience_match(
        self,
        candidate_years: float | None,
        required_years: float | None,
    ) -> float:
        if required_years is None:
            return 100.0
        if candidate_years is None:
            return 50.0
        ratio = candidate_years / required_years
        if ratio >= 1.0:
            return 100.0
        if ratio >= 0.7:
            return 75.0
        if ratio >= 0.5:
            return 50.0
        return 25.0
    
    
    def _github_relevance(self, activity: DeveloperActivity, job: Job) -> float:
        job_terms = set(
            (job.title+ " "+job.description+ " " + " ".join(job.required_skills))
            .lower().split()
        )
        score = 0.0
        
        # Repo topics match
        all_topics = {t.lower() for r in activity.repositories for t in r.topics}
        topic_match = len(all_topics & job_terms) / max(len(job_terms), 1)
        score += topic_match * 50
        
        # Active repos match
        if activity.profile.public_repos >= 5:
            score += 20
        if activity.total_stars >= 10:
            score += 15
        if sum(activity.commit_activity) >= 50:
            score += 15
        return round(min(score, 100.0), 1)                         
        
        
    def _language_match(self, activity: DeveloperActivity, job: Job) -> float:
        job_text = (job.description+ " " + " ".join(job.required_skills))    
        candidate_langs = {l.lower() for l in activity.language_distribution.keys()}
        matched = sum(1 for l in candidate_langs if l in job_text)
        if not candidate_langs:
            return 50.0
        return round(min(matched / max(len(candidate_langs), 1) * 100 * 1.5, 100.0), 1)
    
    @staticmethod
    def _match_level(score: float) -> str:
        if score >= 80: return "Excellent"
        if score >= 65: return "Good"
        if score >= 45: return "Moderate"
        return "Poor"
    
    async def _generate_explanation(
        self,
        resume: ParsedResume,
        activity: DeveloperActivity,
        job: Job,
        score: float,
        skill_data: dict,
        experience_match: float,
    ) -> str:
        prompt = f"""Write a 2-sentence recruiter assessment of fit between this candidate and job.
Be speific about strengths and gaps. No bullet points.float

Job: {job.title} at {job.company or "company"}
Required skills: {", ".join(job.required_skills[:8])}
Required experience: {job.experience_years or "not specified"} years

Candidate: {resume.name}
Skills: {", ".join(resume.skills[:8])}
Experience: {resume.years_of_experience or "unknown"} years
Github languages: {", ".join(list(activity.language_distribution.keys())[:4])}
Matched skills: {", ".join(skill_data["matched"][:6] or "none")}
Missing skills: {", ".join(skill_data["missing"][:6]) or "none"}
Compatibility score: {score}/100"""

        try:
            response =- await self._client.chat.completion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            matched = ", ".join(skill_data["matched"][:3]) or "some skills"
            missing = ", ".join(skill_data["missing"][:3]) or "few gaps"
            return (
                f"Candidate matches on {matched} with a compatibility score of {score}/100. "
                f"Key gaps include {missing}"
            )


