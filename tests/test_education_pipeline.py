import pytest
from pipelines.education_pipeline import (
    _build_prompt,
    _SECTION_LABELS,
    _SYSTEM,
    _TOKEN_CAP,
)


class TestEducationTokenCaps:
    """Verify adaptive token budgets for education pipeline."""

    def test_low_cap(self):
        assert _TOKEN_CAP["low"] == 400

    def test_medium_cap(self):
        assert _TOKEN_CAP["medium"] == 1200

    def test_high_cap(self):
        assert _TOKEN_CAP["high"] == 1200


class TestSectionLabels:
    """Verify all required sections are defined."""

    def test_all_sections_present(self):
        required = {
            "definition",
            "keypoints",
            "working",
            "advantages",
            "disadvantages",
            "applications",
            "example",
            "examtip",
            "diagram",
            "summary",
        }
        assert required.issubset(set(_SECTION_LABELS.keys()))

    def test_definition_label(self):
        assert "DEFINITION" in _SECTION_LABELS["definition"]

    def test_working_label(self):
        assert any(word in _SECTION_LABELS["working"] for word in ["WORKING", "PRINCIPLE", "PRINCIPLES"])

    def test_advantages_label(self):
        assert "ADVANTAGES" in _SECTION_LABELS["advantages"]

    def test_disadvantages_label(self):
        assert "DISADVANTAGES" in _SECTION_LABELS["disadvantages"]

    def test_applications_label(self):
        assert "APPLICATIONS" in _SECTION_LABELS["applications"]

    def test_summary_label(self):
        assert any(word in _SECTION_LABELS["summary"] for word in ["SUMMARY", "CONCLUSION"])


class TestBuildPrompt:
    """Verify _build_prompt includes all required sections per complexity."""

    def test_low_complexity_has_definition_and_keypoints(self):
        prompt = _build_prompt("DBMS", "low")
        assert "DEFINITION:" in prompt
        assert "KEY POINTS:" in prompt
        assert "WORKING:" in prompt
        assert "SUMMARY:" in prompt

    def test_low_complexity_does_not_have_advantages(self):
        prompt = _build_prompt("DBMS", "low")
        assert "ADVANTAGES:" not in prompt
        assert "DISADVANTAGES:" not in prompt
        assert "APPLICATIONS:" not in prompt
        assert "EXAMPLE:" not in prompt
        assert "EXAM TIP:" not in prompt

    def test_medium_complexity_has_all_sections(self):
        prompt = _build_prompt("DBMS", "medium")
        assert "DEFINITION:" in prompt
        assert "KEY POINTS:" in prompt
        assert "WORKING:" in prompt
        assert "ADVANTAGES:" in prompt
        assert "DISADVANTAGES:" in prompt
        assert "APPLICATIONS:" in prompt
        assert "EXAMPLE:" in prompt
        assert "EXAM TIP:" in prompt
        assert "SUMMARY:" in prompt

    def test_high_complexity_has_diagram(self):
        prompt = _build_prompt("DBMS", "high")
        assert "DEFINITION:" in prompt
        assert "DIAGRAM:" in prompt
        assert "SUMMARY:" in prompt

    def test_no_bold_markdown_instruction(self):
        prompt = _build_prompt("DBMS", "medium")
        assert "Do NOT use bold" in prompt


class TestSystemPrompt:
    """Verify _SYSTEM includes exam-oriented instructions."""

    def test_includes_all_required_sections(self):
        assert "definition" in _SYSTEM.lower()
        assert "working" in _SYSTEM.lower()
        assert "advantages" in _SYSTEM.lower()
        assert "disadvantages" in _SYSTEM.lower()
        assert "applications" in _SYSTEM.lower()
        assert "example" in _SYSTEM.lower()
        assert "summary" in _SYSTEM.lower()

    def test_includes_btech_instruction(self):
        assert "B.Tech" in _SYSTEM

    def test_instructs_not_to_skip_sections(self):
        assert "Do not skip any section" in _SYSTEM
