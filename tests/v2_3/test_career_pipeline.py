"""P0 regression test for the career pipeline.

The career pipeline must return ``CareerRoadmapData`` (a structured
``PipelineResult.data`` payload) and must NOT silently fall back to
``general_pipeline`` when a roadmap is successfully generated.
"""

import pytest

from backend.models.response_models import CareerRoadmapData, RoadmapNode


def test_career_pipeline_returns_roadmap_data(monkeypatch):
    """career_pipeline must return CareerRoadmapData, not fall back to general."""
    from backend.models.response_models import CareerRoadmapData, RoadmapNode
    mock_roadmap = CareerRoadmapData(
        roadmap_steps=[RoadmapNode(title="Step 1", description="Learn Python",
                                   estimated_duration="1 month")],
    )
    monkeypatch.setattr("pipelines.career_pipeline.generate_roadmap",
                        lambda q: mock_roadmap)
    from pipelines.career_pipeline import process_query
    result = process_query("How to become a software engineer")
    assert result.data is not None
    assert isinstance(result.data, CareerRoadmapData)
    assert len(result.data.roadmap_steps) > 0
