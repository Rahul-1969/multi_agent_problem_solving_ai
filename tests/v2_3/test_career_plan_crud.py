import pytest
from backend.services.career_plan_service import career_plan_service
from backend.models.response_models import CareerRoadmapData
from backend.auth.user_store import user_store

def test_career_plan_crud():
    # Setup
    username = "testuser_crud"
    user_store.create_user(username, "Test User", "test@test.com", "password")
    
    # Save
    roadmap = CareerRoadmapData()
    plan = career_plan_service.save(username, "Frontend Developer", roadmap)
    assert plan is not None
    assert plan["career_goal"] == "Frontend Developer"
    plan_id = plan["id"]
    
    # Get
    fetched = career_plan_service.get_by_id(username, plan_id)
    assert fetched is not None
    assert fetched["id"] == plan_id
    
    # Rename
    renamed = career_plan_service.rename(username, plan_id, "Senior Frontend Developer")
    assert renamed["career_goal"] == "Senior Frontend Developer"
    
    # Duplicate
    dup = career_plan_service.duplicate(username, plan_id)
    assert dup is not None
    assert dup["id"] != plan_id
    assert "Copy" in dup["career_goal"]
    
    # Delete
    assert career_plan_service.delete(username, plan_id) is True
    assert career_plan_service.get_by_id(username, plan_id) is None
