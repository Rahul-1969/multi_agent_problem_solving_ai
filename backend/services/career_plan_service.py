import uuid
import json
from datetime import datetime
from backend.auth.user_store import user_store
from backend.models.response_models import CareerRoadmapData
from backend.providers.provider_factory import get_provider

class CareerPlanService:
    def get_all(self, username: str) -> list[dict]:
        user = user_store.get_user(username)
        if not user: return []
        return user.get("career_plans", [])
        
    def get_by_id(self, username: str, plan_id: str) -> dict | None:
        plans = self.get_all(username)
        for p in plans:
            if p.get("id") == plan_id:
                return p
        return None

    def save(self, username: str, career_goal: str, roadmap: CareerRoadmapData) -> dict | None:
        user = user_store.get_user(username)
        if not user: return None
        
        plans = user.get("career_plans", [])
        new_plan = {
            "id": str(uuid.uuid4()),
            "career_goal": career_goal,
            "roadmap": roadmap.model_dump(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        plans.append(new_plan)
        user_store.update_career_plans(username, plans)
        return new_plan
        
    def rename(self, username: str, plan_id: str, new_goal: str) -> dict | None:
        plans = self.get_all(username)
        for p in plans:
            if p.get("id") == plan_id:
                p["career_goal"] = new_goal
                p["updated_at"] = datetime.utcnow().isoformat()
                user_store.update_career_plans(username, plans)
                return p
        return None
        
    def delete(self, username: str, plan_id: str) -> bool:
        plans = self.get_all(username)
        initial_len = len(plans)
        plans = [p for p in plans if p.get("id") != plan_id]
        if len(plans) < initial_len:
            user_store.update_career_plans(username, plans)
            return True
        return False
        
    def duplicate(self, username: str, plan_id: str) -> dict | None:
        p = self.get_by_id(username, plan_id)
        if not p: return None
        
        import copy
        new_plan = copy.deepcopy(p)
        new_plan["id"] = str(uuid.uuid4())
        new_plan["career_goal"] = new_plan["career_goal"] + " (Copy)"
        new_plan["created_at"] = datetime.utcnow().isoformat()
        new_plan["updated_at"] = datetime.utcnow().isoformat()
        
        plans = self.get_all(username)
        plans.append(new_plan)
        user_store.update_career_plans(username, plans)
        return new_plan
        
    def regenerate_node(self, username: str, plan_id: str, node_idx: int) -> dict | None:
        p = self.get_by_id(username, plan_id)
        if not p: return None
        
        roadmap_dict = p.get("roadmap", {})
        steps = roadmap_dict.get("roadmap_steps", [])
        if not (0 <= node_idx < len(steps)):
            return None
            
        node = steps[node_idx]
        title = node.get("title", "")
        
        provider = get_provider("career")
        prompt = f"""
        You are an expert career counselor. We are regenerating a specific step in a career roadmap.
        
        Original Step Context:
        Title: {title}
        
        Please generate a new, detailed step for this milestone.
        
        Output Strictly as JSON:
        {{
            "title": "{title} (Alternative)",
            "description": "...",
            "estimated_duration": "...",
            "skills": ["...", "..."],
            "resources": ["...", "..."],
            "certifications": ["..."],
            "projects": ["..."],
            "milestone": "..."
        }}
        """
        
        resp = provider.generate(prompt)
        try:
            if "```json" in resp:
                resp = resp.split("```json")[1].split("```")[0].strip()
            elif "```" in resp:
                resp = resp.split("```")[1].strip()
                
            new_node = json.loads(resp)
            steps[node_idx] = new_node
            p["updated_at"] = datetime.utcnow().isoformat()
            
            plans = self.get_all(username)
            for idx, plan in enumerate(plans):
                if plan.get("id") == plan_id:
                    plans[idx] = p
                    break
                    
            user_store.update_career_plans(username, plans)
            return p
        except Exception:
            return None

    def regenerate_roadmap(self, username: str, plan_id: str) -> dict | None:
        p = self.get_by_id(username, plan_id)
        if not p: return None
        
        goal = p.get("career_goal", "")
        # Re-run the main career roadmap prompt
        from backend.prompts.prompt_loader import load_prompt
        from backend.models.user_models import ProfileData
        
        user = user_store.get_user(username)
        profile_data = ProfileData(**(user.get("profile", {}) if user else {}))
        
        from tools.context_builder import build_user_context
        context = build_user_context(profile_data)
        
        prompt_template = load_prompt("career", "career_roadmap.txt")
        prompt = prompt_template.format(context=context, career_goal=goal)
        
        provider = get_provider("career")
        resp = provider.generate(prompt)
        
        try:
            if "```json" in resp:
                resp = resp.split("```json")[1].split("```")[0].strip()
            elif "```" in resp:
                resp = resp.split("```")[1].strip()
                
            new_roadmap = json.loads(resp)
            p["roadmap"] = new_roadmap
            p["updated_at"] = datetime.utcnow().isoformat()
            
            plans = self.get_all(username)
            for idx, plan in enumerate(plans):
                if plan.get("id") == plan_id:
                    plans[idx] = p
                    break
                    
            user_store.update_career_plans(username, plans)
            return p
        except Exception:
            return None

career_plan_service = CareerPlanService()
