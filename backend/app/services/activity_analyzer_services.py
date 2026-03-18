from app.models.github_activity_model import DeveloperActivity

class ActivityAnalyzerService:
    """
    Computes a normalized developer score (0-100) from Github activity.
    
    Formula:
    score = (commits*0.3) + (repose *0.2) + (stars*0.2) + (recent_activity*0.3)
    
    Each component is normalized to 1-100 before weighting.
    """
    
    CEILINGS = {
        "commits": 500,
        "repos": 50,
        "stars":10_000,
        "followers": 5_000,
        "languages": 5,
    }
    
    def compute_score(self, activity: DeveloperActivity) -> float:
        commit_total = sum(activity.commit_activity)
        recent_commits = sum(activity.commit_activity[-3:])  #last 3 months
        starts = activity.total_stars
        repos = activity.profile.public_repos
        
        commits_norm = min(commit_total / self.CEILINGS["commits"], 1.0) * 100
        repos_norm = min(repos / self.CEILINGS["repos"], 1.0) * 100
        stars_norm = min(starts / self.CEILINGS["stars"], 1.0) * 100
        recent_norm = min(recent_commits / self.CEILINGS["commits"], 1.0) * 100
        
        score = (
            commits_norm * 0.30 +
            repos_norm * 0.20 +
            stars_norm * 0.20 + 
            recent_commits * 0.30
        )
        return round(min(score, 100.0), 1)
    
    
    def grade(self, score: float) -> str:
        if score >= 90: return "Elite"
        if score >=75: return "Senior"
        if score >= 55: return "Mid-level"
        if score >= 35: return "junior"
        return "Entry"
    
    
    def breakdown(self, activity: DeveloperActivity) -> dict:
        commit_totals = sum(activity.commit_activity)
        recent_commits = sum(activity.commit_activity[-3:])  #last 3 months
        return {
            "commits_score": round(min(commit_totals / self.CEILINGS["commits"], 1.0) * 100, 1),
            "repos_score": round(min(activity.profile.public_repos / self.CEILINGS["repos"], 1.0) * 100, 1),
            "stars_score": round(min(activity.total_stars / self.CEILINGS["stars"], 1.0) * 100, 1),
            "recent_activity_score": round(min(recent_commits / self.CEILINGS["commits"], 1.0) * 100, 1),
            "followers_score": round(min(activity.profile.followers / self.CEILINGS["followers"], 1.0) * 100, 1),
            "language_diversity_score": round(min(len(activity.language_distribution) / self.CEILINGS["languages"], 1.0) * 100, 1)  
        }
