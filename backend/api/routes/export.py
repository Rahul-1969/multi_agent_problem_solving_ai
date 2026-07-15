import base64
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any
from backend.services.export_service import export_registry
from backend.models.response_models import ExportResult, CollegeData, CareerRoadmapData, ResumeMatchData, ScholarshipData
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.cache.usage_tracker import usage_tracker

router = APIRouter(prefix="/api/v1/export", tags=["export"])

class ExportRequest(BaseModel):
    export_type: str
    title: str
    data: dict[str, Any]

@router.post("/{format}", response_model=ExportResult, summary="Export structured data")
def export_data(format: str, request: ExportRequest, current_user: TokenPayload = Depends(get_current_user)):
    try:
        # Reconstruct the Pydantic model based on export_type
        if request.export_type == "college_comparison":
            model = CollegeData(**request.data)
        elif request.export_type == "career_roadmap":
            model = CareerRoadmapData(**request.data)
        elif request.export_type == "resume_match":
            model = ResumeMatchData(**request.data)
        elif request.export_type == "scholarships":
            model = ScholarshipData(**request.data)
        else:
            # Fallback to generic BaseModel wrapper if unknown but valid dict
            class GenericData(BaseModel):
                class Config:
                    extra = "allow"
            model = GenericData(**request.data)
            
        try:
            exporter = export_registry.get_exporter(format)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        file_bytes = exporter.export(request.title, model, request.export_type)
        
        # Return base64 encoded data
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        
        safe_title = request.title.replace(" ", "_").lower()
        
        usage_tracker.track_event(current_user.username, "export_downloaded")
        
        return ExportResult(
            base64_data=base64_data,
            filename=f"{safe_title}.{format}"
        )
    except Exception as e:
        usage_tracker.track_event(current_user.username, f"{format}_export_failed")
        raise HTTPException(status_code=400, detail=str(e))
