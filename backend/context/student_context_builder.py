"""
backend/context/student_context_builder.py

Builds student context string for LLM injection.
"""
from dataclasses import dataclass
from typing import List, Optional
from backend.auth.user_store import user_store

@dataclass
class StudentContext:
    semester: Optional[str] = None
    branch: Optional[str] = None
    college: Optional[str] = None
    goal: Optional[str] = None
    weak_subjects: Optional[List[str]] = None
    preferred_language: Optional[str] = None
    saved_colleges: Optional[List[str]] = None
    name: Optional[str] = None

    def to_prompt_context(self) -> str:
        parts = []
        if self.name:
            parts.append(f"Student Name: {self.name}")
        if self.semester:
            parts.append(f"Semester/Academic Year: {self.semester}")
        if self.branch:
            parts.append(f"Branch: {self.branch}")
        if self.college:
            parts.append(f"College: {self.college}")
        if self.goal:
            parts.append(f"Career Goal: {self.goal}")
        if self.weak_subjects:
            parts.append(f"Weak Subjects: {', '.join(self.weak_subjects)}")
        if self.preferred_language:
            parts.append(f"Preferred Language: {self.preferred_language}")
        if self.saved_colleges:
            parts.append(f"Saved Colleges: {', '.join(self.saved_colleges)}")
            
        if not parts:
            return "No specific student profile context available."
            
        return "\n".join(parts)


class StudentContextBuilder:
    def build(self, user_id: str) -> StudentContext:
        user = user_store.get_user(user_id)
        if not user:
            return StudentContext()
            
        # Extract profile from user dict
        profile_dict = user.get("profile", {})
        saved_colleges_dicts = user.get("saved_colleges", [])
        saved_colleges = [c.get("college_code") for c in saved_colleges_dicts if c.get("college_code")]
        
        # Profile fields based on backend/models/user_models.py ProfileData
        # TODO: Add college to ProfileData model in a future migration.
        return StudentContext(
            name=user_id, # using username as name
            semester=profile_dict.get("academic_year"),
            branch=profile_dict.get("preferred_branch"),
            college=None, # TODO: Not yet in model
            goal=profile_dict.get("career_goal"),
            weak_subjects=profile_dict.get("weak_subjects"),
            preferred_language=profile_dict.get("preferred_language"),
            saved_colleges=saved_colleges if saved_colleges else None
        )
