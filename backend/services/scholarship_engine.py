from typing import Dict, Any, List
from backend.providers.provider_factory import get_provider
from tools.metadata_loader import load_scholarship_metadata
from backend.models.response_models import ScholarshipData, ScholarshipItem
from backend.models.user_models import ProfileData
from utils.prompt_loader import load_prompt
from tools.context_builder import build_user_context
from utils.logger import get_logger

logger = get_logger(__name__)

def match_scholarships(profile: ProfileData | dict) -> List[Dict[str, Any]]:
    """
    Deterministically filters the scholarships.json metadata based on user profile.
    """
    if isinstance(profile, dict):
        profile = ProfileData(**profile)
        
    metadata = load_scholarship_metadata()
    matches = []
    
    for code, s_data in metadata.items():
        # Example filter logic:
        # Check income
        income_limit = s_data.get("income_limit")
        if income_limit and profile.income is not None:
            if profile.income > income_limit:
                continue # Ineligible
                
        # Check category
        s_category = s_data.get("category", "Any")
        if s_category not in ["Any", "Government", "Central Government", "State Government", "Private", "Minority", "Women", "ST", "SC", "BC", "EWS"]:
            pass # Keep it simple
            
        if s_category in ["Minority", "ST", "SC", "BC", "EWS"] and profile.category:
            if profile.category.upper() != s_category.upper():
                continue # Ineligible
                
        # Check Gender
        s_gender = s_data.get("gender", "Any")
        if s_gender != "Any" and profile.gender:
            if profile.gender.lower() != s_gender.lower():
                continue
                
        # Check state
        s_state = s_data.get("state")
        if s_state and profile.state:
            if profile.state.lower() != s_state.lower():
                continue
                
        # Check disability
        s_disability = s_data.get("disability_required", False)
        if s_disability and not profile.disability:
            continue
            
        matches.append({
            "code": code,
            **s_data,
            "match_score": 90.0 # Placeholder scoring
        })
        
    # Sort by match score
    matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return matches[:5] # Top 5


def enrich_scholarships(matches: List[Dict[str, Any]], profile: ProfileData | dict = None) -> List[ScholarshipItem]:
    """
    Uses Gemini to enrich the summary of each matched scholarship.
    """
    if not matches:
        return []
        
    provider = get_provider("gemini")
    items = []
    
    # Build shared context
    context = build_user_context(profile)
    
    for match in matches:
        summary = match.get("summary")
        if not summary:
            try:
                # Use Gemini to generate a simplified summary of eligibility
                prompt = load_prompt("scholarships/scholarship_enrichment.txt")
                if not prompt:
                    prompt = "Summarize the following eligibility criteria simply for this profile: {context}\n\n{eligibility}"
                    
                formatted = prompt.format(eligibility=match.get("eligibility", ""), context=context)
                response = provider.generate(formatted)
                summary = response.text if response and response.text else "N/A"
            except Exception as e:
                logger.error(f"Failed to enrich scholarship: {e}")
                summary = "Failed to load summary."
                
        items.append(ScholarshipItem(
            scholarship_name=match.get("scholarship_name", "Unknown"),
            provider=match.get("provider", "Unknown"),
            eligibility=match.get("eligibility", "N/A"),
            amount=match.get("amount", "TBD"),
            deadline=match.get("deadline", "TBD"),
            renewable=match.get("renewable", False),
            match_score=match.get("match_score"),
            eligibility_status=match.get("eligibility_status"),
            summary=summary,
            official_link=match.get("official_link")
        ))
        
    return items

def process_scholarship_request(profile: ProfileData | dict) -> ScholarshipData:
    """
    Orchestrates the deterministic filtering and enrichment.
    """
    matches = match_scholarships(profile)
    enriched_items = enrich_scholarships(matches, profile)
    
    return ScholarshipData(scholarships=enriched_items)

def evaluate_bookmarked_scholarships(bookmark_ids: List[str], profile: ProfileData | dict) -> ScholarshipData:
    """
    Evaluates only the specified bookmarked scholarships against the user's current profile.
    """
    if isinstance(profile, dict):
        profile = ProfileData(**profile)
        
    metadata = load_scholarship_metadata()
    matches = []
    
    for code in bookmark_ids:
        s_data = metadata.get(code)
        if not s_data:
            continue
            
        # Re-run eligibility deterministic checks
        eligible_conditions = 0
        total_conditions = 0
        
        income_limit = s_data.get("income_limit")
        if income_limit and profile.income is not None:
            total_conditions += 1
            if profile.income <= income_limit:
                eligible_conditions += 1
                
        s_category = s_data.get("category", "Any")
        if s_category in ["Minority", "ST", "SC", "BC", "EWS"] and profile.category:
            total_conditions += 1
            if profile.category.upper() == s_category.upper():
                eligible_conditions += 1
                
        s_gender = s_data.get("gender", "Any")
        if s_gender != "Any" and profile.gender:
            total_conditions += 1
            if profile.gender.lower() == s_gender.lower():
                eligible_conditions += 1
                
        s_state = s_data.get("state")
        if s_state and profile.state:
            total_conditions += 1
            if profile.state.lower() == s_state.lower():
                eligible_conditions += 1
                
        s_disability = s_data.get("disability_required", False)
        if s_disability:
            total_conditions += 1
            if profile.disability:
                eligible_conditions += 1
                
        if total_conditions == 0:
            eligibility_status = "Eligible"
        elif eligible_conditions == total_conditions:
            eligibility_status = "Eligible"
        elif eligible_conditions > 0 and eligible_conditions >= total_conditions - 1:
            eligibility_status = "Nearly Eligible"
        else:
            eligibility_status = "Not Eligible"
            
        matches.append({
            "code": code,
            **s_data,
            "match_score": 100.0 if eligibility_status == "Eligible" else (50.0 if eligibility_status == "Nearly Eligible" else 0.0),
            "eligibility_status": eligibility_status
        })
        
    enriched_items = enrich_scholarships(matches, profile)
    return ScholarshipData(scholarships=enriched_items)

