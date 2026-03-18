import re
from typing import Optional

GITHUB_URL_PATTERNS = [
    r'https?://(?:www\.)?github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?)',
    r'(?:^|\s)github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?)',
    r'[Gg]it[Hh]ub[:\s@]+([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?)',
]

RESERVED_PATHS = frozenset({
    "orgs", "topics", "explore", "login", "settings", "marketplace",
    "features", "enterprise", "about", "contact", "pricing", "apps",
    "actions", "sponsors", "security", "notifications", "issues",
    "pulls", "discussions", "trending", "collections",
})

def extract_github_username(text: str) -> Optional[str]:
    """
    Extract a Github username from a URL string or free text.
    Returns the username string or None if not found.
    """
    if not text:
        return None
    
    for pattern in GITHUB_URL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            username = match.group(1).rstrip("/")
            if username.lower() not in RESERVED_PATHS and len(username) >=1:
                return username
            
    return None

def extract_email(text: str) -> Optional[str]:
    """
    Extract first email address from text.
    """
    match = re.search(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b', text)
    return match.group(0) if match else None

def extract_linkedin(text: str):
    """
    Extract LinkedIn profile URL from text.
    """
    match = re.search(
        r'https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_%]+)',
        text, re.IGNORECASE
    )
    return match.group(0) if match else None