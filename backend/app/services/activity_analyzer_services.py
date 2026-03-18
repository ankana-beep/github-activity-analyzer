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
    
