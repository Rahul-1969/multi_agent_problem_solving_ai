"""
backend/models/response_models.py
Structured Pydantic response models.

Every domain returns a typed 'data' dict instead of a raw string.
The raw formatted string is also included as 'response' for
backward compatibility with clients that already use it.
"""

from typing import Any, Final, Literal, TypeAlias

from constants.domains import (
    COLLEGE_DOMAIN,
    MEDICAL_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
    LIVE_DOMAIN,
    CAREER_DOMAIN,
    SCHOLARSHIP_DOMAIN,
    RESUME_DOMAIN,
)
from pydantic import BaseModel, Field, ConfigDict, model_validator


# Module constants and type aliases
MEDICAL_DISCLAIMER: Final[str] = (
    "This is AI-generated information only, NOT medical advice."
)

MODEL_CONFIG: Final = ConfigDict(extra="forbid")

DomainType = Literal[
    COLLEGE_DOMAIN,
    MEDICAL_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
    LIVE_DOMAIN,
    CAREER_DOMAIN,
    SCHOLARSHIP_DOMAIN,
    RESUME_DOMAIN,
]

# Domain-specific models


class EducationData(BaseModel):
    model_config = MODEL_CONFIG

    topic: str
    definition: str | None = None
    key_points: str | None = None
    example: str | None = None
    exam_tip: str | None = None

    # Expanded education fields
    working: str | None = None
    advantages: str | None = None
    disadvantages: str | None = None
    applications: str | None = None
    summary: str | None = None

    # Frontend compatibility fields (P0-10)
    title: str | None = None
    explanation: str | None = None
    diagram: str | None = None
    key_formulas: list[str] | None = None
    tips: list[str] | None = None


class MedicalData(BaseModel):
    model_config = MODEL_CONFIG

    conditions: str | None = None
    treatments: str | None = None
    lifestyle: str | None = None
    emergency: str | None = None
    disclaimer: str = MEDICAL_DISCLAIMER

    # Frontend compatibility fields (P0-10)
    symptoms: str | None = None
    possible_causes: list[str] | None = None
    recommendations: str | None = None
    when_to_consult: str | None = None


class CodingData(BaseModel):
    model_config = MODEL_CONFIG

    language: str | None = None
    code: str | None = None
    explanation: str | None = None
    complexity: str | None = None
    tip: str | None = None
    clarification: list[str] | None = None

    # Frontend compatibility fields (P0-10)
    title: str | None = None
    time_complexity: str | None = None
    space_complexity: str | None = None
    output: str | None = None
    key_points: list[str] | None = None


class CollegeCard(BaseModel):
    """Rich structured object for a single predicted college."""

    model_config = MODEL_CONFIG

    # ── Identity ──────────────────────────────────────────────────────────────
    college_name: str
    college_code: str
    location: str = "Telangana"

    # ── Classification ────────────────────────────────────────────────────────
    autonomous: bool = False
    affiliated_to: str = "JNTUH"
    college_type: str = "Private"          # "Private" | "Government" | "Deemed"

    # ── Accreditation ─────────────────────────────────────────────────────────
    naac_grade: str = "N/A"
    nba_accredited: bool = False
    nirf_rank: int | None = None
    established: int | None = None

    # ── Branches ──────────────────────────────────────────────────────────────
    predicted_branches: list[str] = Field(default_factory=list)   # matched by predictor
    available_branches: list[str] = Field(default_factory=list)   # all college branches

    # ── Cutoff context ────────────────────────────────────────────────────────
    closing_rank: int | None = None          # last year's closing rank
    score_above_cutoff: int | None = None    # user_rank - closing_rank (positive = safer)

    # ── Probability ───────────────────────────────────────────────────────────
    admission_probability: str = "SAFE"      # "SAFE" | "MODERATE" | "DREAM"
    recommendation_level: str = ""           # "High Chance" | "Good Chance" | "Lower Chance"

    # ── Placements ────────────────────────────────────────────────────────────
    placement_percentage: float | None = None
    avg_package_lpa: float | None = None
    highest_package_lpa: float | None = None
    median_package_lpa: float | None = None
    top_recruiters: list[str] = Field(default_factory=list)

    # ── Facilities & Cost ─────────────────────────────────────────────────────
    hostel_available: bool = False
    scholarships_available: bool = False
    tuition_fee_per_year: int | None = None
    hostel_fee: int | None = None
    transport_available: bool | None = None
    campus_area_acres: float | None = None
    minority_status: bool = False
    contact_number: str | None = None
    official_email: str | None = None

    # ── Decision Support (Phase 6) ────────────────────────────────────────────
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    best_for: str | None = None
    ideal_student_profile: str | None = None
    career_opportunities: str | None = None
    campus_highlights: list[str] = Field(default_factory=list)
    internships_available: str | None = None
    parent_summary: str | None = None

    # ── Links & Media ─────────────────────────────────────────────────────────
    official_website: str | None = None
    google_maps_url: str | None = None
    college_image_url: str | None = None

    # ── AI explanation & Ranking ──────────────────────────────────────────────
    reason_for_recommendation: str = ""
    ranking_score: float | None = None
    medal_badge: str | None = None
    is_best_match: bool = False

    # ── Phase 10 Extended Intelligence ────────────────────────────────────────
    student_match_score: float | None = None
    roi_score: float | None = None
    roi_label: str | None = None
    campus_rating_stars: int | None = None
    prediction_confidence: str | None = None
    counselor_summary: dict | None = Field(default_factory=dict)
    comparison_ready: dict | None = Field(default_factory=dict)
    ranking_breakdown: dict | None = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    final_verdict: str | None = None


class CollegeData(BaseModel):
    model_config = MODEL_CONFIG

    rank: int | None = None
    category: str | None = None
    gender: str | None = None
    branch: str | None = None
    location: str | None = None
    exam: str = "EAMCET 2025"
    safe: list[CollegeCard] = Field(default_factory=list)
    moderate: list[CollegeCard] = Field(default_factory=list)
    dream: list[CollegeCard] = Field(default_factory=list)


class GeneralData(BaseModel):
    model_config = MODEL_CONFIG

    answer: str


class ScholarshipItem(BaseModel):
    model_config = MODEL_CONFIG

    scholarship_name: str
    provider: str
    eligibility: str
    amount: str
    deadline: str
    renewable: bool = False
    match_score: float | None = None
    eligibility_status: str | None = None
    summary: str | None = None
    official_link: str | None = None


class ScholarshipData(BaseModel):
    model_config = MODEL_CONFIG

    scholarships: list[ScholarshipItem] = Field(default_factory=list)


class RoadmapNode(BaseModel):
    model_config = MODEL_CONFIG

    title: str
    description: str
    estimated_duration: str
    skills: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    milestone: str | None = None

class CareerRoadmapData(BaseModel):
    model_config = MODEL_CONFIG

    roadmap_steps: list[RoadmapNode] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    books: list[str] = Field(default_factory=list)
    youtube_channels: list[str] = Field(default_factory=list)
    github_projects: list[str] = Field(default_factory=list)
    practice_platforms: list[str] = Field(default_factory=list)
    internship_strategy: str | None = None
    interview_preparation: str | None = None
    salary_progression: str | None = None
    top_companies: list[str] = Field(default_factory=list)
    skills_per_stage: dict | None = Field(default_factory=dict)
    timeline: str | None = None


class ResumeData(BaseModel):
    model_config = MODEL_CONFIG

    ats_score: int | None = None
    resume_summary: str | None = None
    missing_skills: list[str] = Field(default_factory=list)
    detected_skills: list[str] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    education: list[dict] = Field(default_factory=list)
    grammar_issues: list[str] = Field(default_factory=list)
    weak_bullet_points: list[str] = Field(default_factory=list)
    formatting_suggestions: list[str] = Field(default_factory=list)
    suggested_certifications: list[str] = Field(default_factory=list)
    suggested_improvements: list[str] = Field(default_factory=list)
    future_ready_skills: list[str] = Field(default_factory=list)

class JobDescriptionData(BaseModel):
    model_config = MODEL_CONFIG

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience: str | None = None
    education: str | None = None
    certifications: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    location: str | None = None
    employment_type: str | None = None
    salary_range: str | None = None

class ResumeMatchData(BaseModel):
    model_config = MODEL_CONFIG

    overall_match_score: int | None = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    experience_gap: str | None = None
    education_gap: str | None = None
    certification_gap: str | None = None
    project_gap: str | None = None
    ATS_score: int | None = None
    improvement_priority: list[str] = Field(default_factory=list)
    recommended_courses: list[str] = Field(default_factory=list)
    recommended_projects: list[str] = Field(default_factory=list)
    gemini_suggestions: str | None = None

class SavedCareerPlanData(BaseModel):
    model_config = MODEL_CONFIG

    plans: list[Any] = Field(default_factory=list) # Replaced with 'SavedCareerPlan' inside user_models, this wrapper can hold them

class ScholarshipBookmarkData(BaseModel):
    model_config = MODEL_CONFIG

    bookmarks: list[Any] = Field(default_factory=list)

class ExportResult(BaseModel):
    model_config = MODEL_CONFIG

    file_url: str | None = None
    base64_data: str | None = None
    filename: str | None = None


# Unified response models


# Precise response data union
ResponseData: TypeAlias = (
    EducationData
    | MedicalData
    | CodingData
    | CollegeData
    | ScholarshipData
    | CareerRoadmapData
    | ResumeData
    | GeneralData
)

class BaseResponse(BaseModel):
    model_config = MODEL_CONFIG

    success: bool
    error: str | None = None


class ChatMessage(BaseModel):
    model_config = MODEL_CONFIG

    sender: str
    content: str
    text: str | None = None
    domain: str | None = None
    data: dict[str, Any] | None = None
    created_at: str | None = None
    # RAG metadata — present on bot messages that used the RAG pipeline;
    # None on user messages and non-RAG bot messages (pre-existing history
    # entries also safely deserialise as None via the default).
    sources: list[str] | None = None
    used_rag: bool | None = None

    @model_validator(mode="before")
    def _fill_text(cls, data):
        if isinstance(data, dict) and data.get("text") is None:
            data["text"] = data.get("content")
        return data



class ChatSummary(BaseModel):
    model_config = MODEL_CONFIG

    id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None
    last_message: str | None = None


class ChatDetailResponse(BaseResponse):
    model_config = MODEL_CONFIG

    chat_id: str
    title: str
    messages: list[ChatMessage] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
    last_message: str | None = None


class ChatListResponse(BaseResponse):
    model_config = MODEL_CONFIG

    chats: list[ChatSummary] = Field(default_factory=list)


class ChatResponse(BaseResponse):
    model_config = MODEL_CONFIG

    chat_id: str | None = None
    domain: DomainType
    data: ResponseData | None = None  # typed domain data dict
    response: str  # formatted string (backward compat)
    messages: list[ChatMessage] | None = None
    chat_title: str | None = None
    sources: list[str] | None = None
    used_rag: bool | None = None


class ErrorResponse(BaseResponse):
    model_config = MODEL_CONFIG

    success: bool = False


class TokenResponse(BaseModel):
    model_config = MODEL_CONFIG

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    username: str | None = None
    name: str | None = None
    email: str | None = None


class RegisterResponse(BaseModel):
    model_config = MODEL_CONFIG

    username: str
    name: str | None = None
    email: str | None = None