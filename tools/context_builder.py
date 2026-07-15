from backend.models.user_models import ProfileData

def build_user_context(user_profile: ProfileData | dict | None) -> str:
    """
    Centralized context builder to format a student profile 
    into a context string for prompt injection into Gemini.
    """
    if not user_profile:
        return "No student profile context available."

    if isinstance(user_profile, dict):
        user_profile = ProfileData(**user_profile)

    context_lines = ["--- Student Profile Context ---"]
    
    if user_profile.preferred_branch:
        context_lines.append(f"- Preferred Branch: {user_profile.preferred_branch}")
    if user_profile.preferred_location:
        context_lines.append(f"- Preferred Location: {user_profile.preferred_location}")
    if user_profile.career_goal:
        context_lines.append(f"- Career Goal: {user_profile.career_goal}")
    if user_profile.academic_year:
        context_lines.append(f"- Academic Year: {user_profile.academic_year}")
    if user_profile.category:
        context_lines.append(f"- Category: {user_profile.category}")
    if user_profile.gender:
        context_lines.append(f"- Gender: {user_profile.gender}")
    if user_profile.disability is not None:
        context_lines.append(f"- Disability: {'Yes' if user_profile.disability else 'No'}")
    if user_profile.income is not None:
        context_lines.append(f"- Annual Income: ₹{user_profile.income}")
    if user_profile.state:
        context_lines.append(f"- State: {user_profile.state}")
        
    if len(context_lines) == 1:
        return "No specific student profile context provided."
        
    context_lines.append("-------------------------------")
    return "\n".join(context_lines)
