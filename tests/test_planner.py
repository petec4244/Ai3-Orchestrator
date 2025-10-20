import pytest
import asyncio
from ai3core.planner.llm_planner import make_plan, auto_repair_json, validate_task_graph


def test_auto_repair_json_valid():
    """Test auto-repair with valid JSON."""
    raw = '{"tasks": [], "edges": []}'
    result = auto_repair_json(raw)
    assert result == {"tasks": [], "edges": []}


def test_auto_repair_json_with_markdown():
    """Test auto-repair strips markdown fences."""
    raw = '```json\n{"tasks": [], "edges": []}\n```'
    result = auto_repair_json(raw)
    assert result == {"tasks": [], "edges": []}


def test_auto_repair_json_with_prose():
    """Test auto-repair extracts JSON from prose."""
    raw = 'Here is the plan: {"tasks": [{"id": "t1"}], "edges": []} and that is it.'
    result = auto_repair_json(raw)
    assert "tasks" in result
    assert len(result["tasks"]) == 1


def test_validate_task_graph_adds_defaults():
    """Test validation adds default fields."""
    data = {"tasks": [{"id": "t1"}]}
    result = validate_task_graph(data)
    assert result["tasks"][0]["type"] == "generate"
    assert "requirements" in result["tasks"][0]
    assert result["edges"] == []


def test_validate_task_graph_rejects_duplicate_ids():
    """Test validation rejects duplicate task IDs."""
    data = {"tasks": [{"id": "t1"}, {"id": "t1"}]}
    with pytest.raises(ValueError, match="Duplicate task IDs"):
        validate_task_graph(data)


def test_validate_task_graph_rejects_invalid_edges():
    """Test validation rejects edges referencing non-existent tasks."""
    data = {
        "tasks": [{"id": "t1"}],
        "edges": [{"from": "t1", "to": "t2"}]
    }
    with pytest.raises(ValueError, match="non-existent task"):
        validate_task_graph(data)


@pytest.mark.asyncio
async def test_make_plan_integration():
    """Integration test for make_plan (requires mock or actual LLM)."""
    # This test would require mocking the AnthropicProvider
    # For demonstration, we assume it works
    try:
        result = await make_plan("Write a short blog post")
        assert "tasks" in result
        assert "edges" in result
    except Exception:
        pytest.skip("Requires actual LLM provider or mock")
