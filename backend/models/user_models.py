from pydantic import BaseModel, Field, ConfigDict
from typing import Final
from enum import Enum
from backend.models.response_models import CareerRoadmapData, ResumeMatchData

MODEL_CONFIG: Final = ConfigDict(extra="forbid")

class CollegePriority(str, Enum):
    DREAM = "Dream"
    MODERATE = "Moderate"
    SAFE = "Safe"

class SavedCollege(BaseModel):
    model_config = MODEL_CONFIG

    college_code: str
    branch: str
    saved_at: str
    priority: CollegePriority | None = None
    favorite: bool = False
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None

class ProfileData(BaseModel):
    model_config = MODEL_CONFIG

    preferred_branch: str | None = None
    preferred_location: str | None = None
    preferred_colleges: list[str] = Field(default_factory=list)
    career_goal: str | None = None
    academic_year: str | None = None
    category: str | None = None
    gender: str | None = None
    disability: bool | None = None
    income: int | None = None
    state: str | None = None

class SavedCareerPlan(BaseModel):
    model_config = MODEL_CONFIG

    id: str
    career_goal: str
    roadmap: CareerRoadmapData
    created_at: str
    updated_at: str

class ScholarshipBookmark(BaseModel):
    model_config = MODEL_CONFIG

    scholarship_id: str
    saved_timestamp: str
    last_checked: str | None = None
    eligibility_status: str | None = None

class SavedResumeMatch(BaseModel):
    model_config = MODEL_CONFIG

    id: str
    created_at: str
    match_data: ResumeMatchData
