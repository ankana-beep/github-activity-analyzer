from fastapi import UploadFile, HTTPException

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def validate_resume_file(file: UploadFile, max_size_mb: int = 10) -> None:
    """
    Validates that the uploaded file is a PDF or DOCX and within size limits.
    Raises HTTPException on failure.
    """
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Only PDF and DOCX are accepted."
        )
        
        
def check_file_size(content: bytes, max_size_mb: int = 10) -> None:
    if len(content) > max_size_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {max_size_mb} MB limit.")
        