from fastapi import APIRouter, File, UploadFile, Depends, Form
from backend.services.resume_service import analyze_resume_text
from backend.pipelines.resume_match_pipeline import ResumeMatchPipeline
from utils.logger import get_logger
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.auth.user_store import user_store
from backend.models.user_models import ProfileData

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/resume")

@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Parses an uploaded PDF/DOCX resume, extracts text, 
    and returns a structured ResumeData analysis.
    """
    try:
        if not file.filename:
            return {"status": "error", "message": "No filename"}
        
        safe_filename = file.filename.lower()
        if not safe_filename.endswith(".pdf") and not safe_filename.endswith(".docx"):
            return {"status": "error", "message": "Only PDF and DOCX files are supported."}
            
        content = await file.read()
        
        # We need a temporary way to extract text from raw bytes or save it temp
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{safe_filename.split('.')[-1]}") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
            
        try:
            from tools.document_extractor import DocumentExtractor
            raw_text = DocumentExtractor.extract_text(tmp_path, safe_filename)
        finally:
            os.unlink(tmp_path)
            
        resume_data = analyze_resume_text(raw_text)
        from backend.cache.usage_tracker import usage_tracker
        usage_tracker.track_event("anonymous", "resume_uploaded")
        
        return {
            "status": "success",
            "data": resume_data.model_dump()
        }
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Parses an uploaded PDF/DOCX resume and compares it against JD text deterministically.
    """
    try:
        if not file.filename:
            return {"status": "error", "message": "No filename"}
        
        safe_filename = file.filename.lower()
        if not safe_filename.endswith(".pdf") and not safe_filename.endswith(".docx"):
            return {"status": "error", "message": "Only PDF and DOCX files are supported."}
            
        content = await file.read()
        
        user_record = user_store.get_user(current_user.username)
        profile = ProfileData(**user_record.get("profile", {})) if user_record else None
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{safe_filename.split('.')[-1]}") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
            
        try:
            pipeline_result = ResumeMatchPipeline.execute(tmp_path, safe_filename, jd_text, profile)
        finally:
            os.unlink(tmp_path)
            
        from backend.cache.usage_tracker import usage_tracker
        usage_tracker.track_event(current_user.username, "resume_uploaded")
        usage_tracker.track_event(current_user.username, "resume_match")
            
        return {
            "status": "success",
            "response": pipeline_result.response,
            "data": pipeline_result.data
        }
    except Exception as e:
        logger.error(f"Resume matching failed: {e}")
        return {"status": "error", "message": str(e)}
