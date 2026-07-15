from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.auth.user_store import user_store
from backend.models.user_models import ProfileData, SavedCollege, SavedCareerPlan, ScholarshipBookmark, SavedResumeMatch
from backend.models.response_models import SavedCareerPlanData, CareerRoadmapData, ScholarshipData, ResumeMatchData
from backend.services.career_plan_service import career_plan_service
from backend.services.scholarship_engine import evaluate_bookmarked_scholarships
from backend.cache.usage_tracker import usage_tracker
from datetime import datetime

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])

@router.get("", response_model=ProfileData, summary="Get current user's profile")
def get_profile(current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileData(**user.get("profile", {}))

@router.post("", response_model=ProfileData, summary="Update user's profile")
def update_profile(profile_data: ProfileData, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.update_profile(current_user.username, profile_data.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileData(**user.get("profile", {}))

@router.get("/colleges", response_model=List[SavedCollege], summary="Get saved colleges")
def get_saved_colleges(current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [SavedCollege(**c) for c in user.get("saved_colleges", [])]

class SaveCollegeRequest(BaseModel):
    college_code: str
    branch: str
    tags: list[str] | None = None
    notes: str | None = None

@router.post("/colleges", response_model=List[SavedCollege], summary="Save a college")
def save_college(request: SaveCollegeRequest, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    saved = user.get("saved_colleges", [])
    
    # Check if already saved
    for c in saved:
        if c.get("college_code") == request.college_code and c.get("branch") == request.branch:
            # Update tags and notes if provided
            if request.tags is not None:
                c["tags"] = request.tags
            if request.notes is not None:
                c["notes"] = request.notes
            updated_user = user_store.update_saved_colleges(current_user.username, saved)
            return [SavedCollege(**c) for c in updated_user.get("saved_colleges", [])]
            
    new_saved = {
        "college_code": request.college_code,
        "branch": request.branch,
        "saved_at": datetime.utcnow().isoformat(),
        "tags": request.tags or [],
        "notes": request.notes
    }
    saved.append(new_saved)
    
    updated_user = user_store.update_saved_colleges(current_user.username, saved)
    usage_tracker.track_event(current_user.username, "saved_college_added")
    return [SavedCollege(**c) for c in updated_user.get("saved_colleges", [])]

@router.delete("/colleges", response_model=List[SavedCollege], summary="Remove a saved college")
def remove_college(request: SaveCollegeRequest, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    saved = user.get("saved_colleges", [])
    filtered = [c for c in saved if not (c.get("college_code") == request.college_code and c.get("branch") == request.branch)]
    
    updated_user = user_store.update_saved_colleges(current_user.username, filtered)
    usage_tracker.track_event(current_user.username, "saved_college_removed")
    return [SavedCollege(**c) for c in updated_user.get("saved_colleges", [])]

# --- Career Plans ---

@router.get("/career-plans", response_model=SavedCareerPlanData, summary="Get saved career plans")
def get_career_plans(current_user: TokenPayload = Depends(get_current_user)):
    plans = career_plan_service.get_all(current_user.username)
    return SavedCareerPlanData(plans=plans)

@router.get("/career-plans/{plan_id}", response_model=SavedCareerPlan, summary="Get a career plan by ID")
def get_career_plan(plan_id: str, current_user: TokenPayload = Depends(get_current_user)):
    plan = career_plan_service.get_by_id(current_user.username, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    usage_tracker.track_event(current_user.username, "career_plan_opened")
    return SavedCareerPlan(**plan)

class SaveCareerPlanRequest(BaseModel):
    career_goal: str
    roadmap: CareerRoadmapData

@router.post("/career-plans", response_model=SavedCareerPlan, summary="Save a career plan")
def save_career_plan(request: SaveCareerPlanRequest, current_user: TokenPayload = Depends(get_current_user)):
    plan = career_plan_service.save(current_user.username, request.career_goal, request.roadmap)
    if not plan:
        raise HTTPException(status_code=400, detail="Failed to save career plan")
    usage_tracker.track_event(current_user.username, "career_plan_saved")
    return SavedCareerPlan(**plan)

class RenameCareerPlanRequest(BaseModel):
    career_goal: str

@router.put("/career-plans/{plan_id}", response_model=SavedCareerPlan, summary="Rename a career plan")
def rename_career_plan(plan_id: str, request: RenameCareerPlanRequest, current_user: TokenPayload = Depends(get_current_user)):
    plan = career_plan_service.rename(current_user.username, plan_id, request.career_goal)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return SavedCareerPlan(**plan)

@router.delete("/career-plans/{plan_id}", summary="Delete a career plan")
def delete_career_plan(plan_id: str, current_user: TokenPayload = Depends(get_current_user)):
    success = career_plan_service.delete(current_user.username, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    usage_tracker.track_event(current_user.username, "career_plan_deleted")
    return {"status": "success"}

@router.post("/career-plans/{plan_id}/duplicate", response_model=SavedCareerPlan, summary="Duplicate a career plan")
def duplicate_career_plan(plan_id: str, current_user: TokenPayload = Depends(get_current_user)):
    plan = career_plan_service.duplicate(current_user.username, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return SavedCareerPlan(**plan)

@router.post("/career-plans/{plan_id}/nodes/{node_idx}/regenerate", response_model=SavedCareerPlan, summary="Regenerate a roadmap node")
def regenerate_career_node(plan_id: str, node_idx: int, current_user: TokenPayload = Depends(get_current_user)):
    plan = career_plan_service.regenerate_node(current_user.username, plan_id, node_idx)
    if not plan:
        raise HTTPException(status_code=400, detail="Failed to regenerate node")
    usage_tracker.track_event(current_user.username, "career_plan_regenerated")
    return SavedCareerPlan(**plan)

@router.post("/career-plans/{plan_id}/regenerate", response_model=SavedCareerPlan, summary="Regenerate entire roadmap")
def regenerate_entire_roadmap(plan_id: str, current_user: TokenPayload = Depends(get_current_user)):
    plan = career_plan_service.regenerate_roadmap(current_user.username, plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Failed to regenerate roadmap")
    usage_tracker.track_event(current_user.username, "career_plan_regenerated")
    return SavedCareerPlan(**plan)

# --- Scholarship Bookmarks ---

class BookmarkScholarshipRequest(BaseModel):
    scholarship_id: str

@router.get("/scholarships", response_model=ScholarshipData, summary="Get bookmarked scholarships")
def get_bookmarked_scholarships(current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    bookmarks = user.get("scholarship_bookmarks", [])
    bookmark_ids = [b.get("scholarship_id") for b in bookmarks]
    profile = user.get("profile", {})
    
    return evaluate_bookmarked_scholarships(bookmark_ids, profile)

@router.post("/scholarships", response_model=list[ScholarshipBookmark], summary="Bookmark a scholarship")
def bookmark_scholarship(request: BookmarkScholarshipRequest, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    bookmarks = user.get("scholarship_bookmarks", [])
    
    # Check if already bookmarked
    if any(b.get("scholarship_id") == request.scholarship_id for b in bookmarks):
        return [ScholarshipBookmark(**b) for b in bookmarks]
        
    bookmarks.append({
        "scholarship_id": request.scholarship_id,
        "saved_timestamp": datetime.utcnow().isoformat()
    })
    
    updated_user = user_store.update_scholarship_bookmarks(current_user.username, bookmarks)
    usage_tracker.track_event(current_user.username, "scholarship_bookmarked")
    return [ScholarshipBookmark(**b) for b in updated_user.get("scholarship_bookmarks", [])]

@router.delete("/scholarships", response_model=list[ScholarshipBookmark], summary="Remove a scholarship bookmark")
def remove_scholarship_bookmark(request: BookmarkScholarshipRequest, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    bookmarks = user.get("scholarship_bookmarks", [])
    filtered = [b for b in bookmarks if b.get("scholarship_id") != request.scholarship_id]
    
    updated_user = user_store.update_scholarship_bookmarks(current_user.username, filtered)
    usage_tracker.track_event(current_user.username, "bookmark_removed")
    return [ScholarshipBookmark(**b) for b in updated_user.get("scholarship_bookmarks", [])]

# --- Resume Matches ---

@router.get("/resume-matches", response_model=List[SavedResumeMatch], summary="Get saved resume matches")
def get_resume_matches(current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [SavedResumeMatch(**m) for m in user.get("resume_matches", [])]

class SaveResumeMatchRequest(BaseModel):
    id: str
    match_data: ResumeMatchData

@router.post("/resume-matches", response_model=SavedResumeMatch, summary="Save a resume match")
def save_resume_match(request: SaveResumeMatchRequest, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    matches = user.get("resume_matches", [])
    
    # Check if already exists
    for m in matches:
        if m.get("id") == request.id:
            return SavedResumeMatch(**m)
            
    new_match = {
        "id": request.id,
        "created_at": datetime.utcnow().isoformat(),
        "match_data": request.match_data.model_dump()
    }
    matches.append(new_match)
    
    user_store.update_resume_matches(current_user.username, matches)
    usage_tracker.track_event(current_user.username, "resume_match_saved")
    return SavedResumeMatch(**new_match)

@router.delete("/resume-matches/{match_id}", summary="Delete a resume match")
def delete_resume_match(match_id: str, current_user: TokenPayload = Depends(get_current_user)):
    user = user_store.get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    matches = user.get("resume_matches", [])
    filtered = [m for m in matches if m.get("id") != match_id]
    
    if len(filtered) == len(matches):
        raise HTTPException(status_code=404, detail="Match not found")
        
    user_store.update_resume_matches(current_user.username, filtered)
    return {"status": "success"}

