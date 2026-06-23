import pytest
from pipelines.general_pipeline import (
    _query_type,
    _TOKEN_CAP,
    general_pipeline,
)
from pipelines.pipeline_result import PipelineResult


class TestQueryTypeClassification:
    """Verify _query_type correctly classifies queries."""

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("Hi there", "conversational"),
            ("Hello!", "conversational"),
            ("Thanks", "conversational"),
            ("Good morning", "conversational"),
            ("What is the capital of India", "factual"),
            ("Who invented the telephone", "general"),
            ("How many states in USA", "factual"),
            ("Capital of France", "factual"),
            ("Define gravity", "factual"),
            ("Explain Newtons Second Law", "explanatory"),
            ("Describe photosynthesis", "explanatory"),
            ("How does a computer work", "explanatory"),
            ("Difference between TCP and UDP", "explanatory"),
            ("Advantages of DBMS", "explanatory"),
            ("Why is the sky blue", "explanatory"),
            ("Tell me something interesting", "general"),
        ],
    )
    def test_query_type(self, query, expected):
        assert _query_type(query) == expected


class TestTokenCaps:
    """Verify adaptive token budgets match requirements."""

    def test_conversational_cap(self):
        assert _TOKEN_CAP["conversational"] == 150

    def test_factual_cap(self):
        assert _TOKEN_CAP["factual"] == 400

    def test_explanatory_cap(self):
        assert _TOKEN_CAP["explanatory"] == 1200

    def test_general_cap(self):
        assert _TOKEN_CAP["general"] == 800


class TestNoAgentChain:
    """Verify explanatory queries use base agent only, not run_agents."""

    def test_no_run_agents_import(self):
        import ast
        import inspect
        import pipelines.general_pipeline as gp

        source = inspect.getsource(gp)
        tree = ast.parse(source)
        imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        for imp in imports:
            module = imp.module or ""
            names = {alias.name for alias in imp.names}
            assert "run_agents" not in names, f"run_agents imported from {module}"

    def test_explanatory_return_type(self, monkeypatch):
        """Explanatory branch returns a PipelineResult."""

        def fake_call_llm(prompt, system, num_predict):
            return "Fake detailed answer."

        monkeypatch.setattr(
            "pipelines.general_pipeline.call_llm", fake_call_llm
        )
        result = general_pipeline("Explain gravity")
        assert isinstance(result, PipelineResult)
        assert result.response == "Fake detailed answer."
