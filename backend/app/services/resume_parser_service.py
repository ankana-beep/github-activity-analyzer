import io
import json
import logging
from openai import AsyncOpenAI
import pdfplumber
from docx import Document
from app.core.config import Settings
from app.models.candidate_model import ParsedResume, Experience, Education
from app.utils.regex_utlis import extract_github_username, extract_email, extract_linkedin

logger = logging.getLogger(__name__)

class ResumeParserService:
    """
    Extracts plain text from PDF/DOCX then uses Claude to parse
    structured data: name, email, skills, experience, education, Github.
    """
    
    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def parse(self, file_bytes: bytes, filename: str) -> ParsedResume:
        logger.info(f"Parsing: {filename}")
        text = self._extract_text(file_bytes, filename)
        return await self._ai_extract(text)
    
    
    # Text extraction
    
    def _extract_text(self, data: bytes, filename: str) -> str:
        if filename.lower().endswith(".pdf"):
            return self._pdf_text(data)
        if filename.lower().endswith(".docx"):
            return self._docx_text(data)
        raise ValueError(f"Unsupported file type: {filename}")
        
    def _pdf_text(self, data: bytes) -> str:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)    
           
    
    def _docx_text(self, data: bytes) -> str:
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    
    
    # AI extraction
    async def _ai_extract(self, text: str) ->ParsedResume:
        prompt = f"""You are a precise resume parser. extract all fields from the resume below.
Return ONLY a valid JSON object - no markdown, no explantaion, no code fences.PermissionError

{{
    "name": "full name or null",
    "email": "email or null",
    "phone": "phone number or null",
    "github_url": "full https://github.com/username URL or https://github.com URL or null",
    "linkedin": "LinkedIn URL or null",
    "summary": "professional summarry or null",
    "years_of_experiece": 0.0,
    "skills": ["skill1", "skill2"],
    "experience": [
        {{
            "company": "company name or null",
            "role": "role or null",
            "duration": "duration or null",
            "description": "description or null"
        }},
        {{
            "company": "company name or null",
            "role": "role or null",
            "duration": "duration or null",
            "description": "description or null"
        }}
    ],
    "education": [
        {{"institution": "...", "degree": "...", "year": "..."}}
    ]
}}  

Resume:
{text[:5000]}"""

        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a resume parser."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            raw = response.choices[0].messages.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw.strip())
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            data = {}            
            
        github_url = data.get("github_url")
        username = extract_github_username(github_url or text) 
        
        return ParsedResume(
            name=data.get("name"),
            email=data.get("email") or extract_email(text),
            phone=data.get("phone"),
            github_url=github_url,
            github_username=username,
            linkedin=data.get("linkedin") or extract_linkedin(text),
            skills=data.get("skills", []),
            summary=data.get("summary"),
            years_of_experience=data.get("years_of_experience"),
            experience=[Experience(**e) for e in data.get("experience", []) if isinstance(e, dict)],
            education=[Education(**e) for e in data.get("education", []) if isinstance(e, dict)],
        )   