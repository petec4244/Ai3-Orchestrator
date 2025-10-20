import pytest
from ai3core.executor.scheduler import topological_sort, compute_ready_sets


def test_topological_sort_linear():
    """Test topological sort on linear dependency chain."""
    tasks = [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}]
    edges = [{"from": "t1", "to": "t2"}, {"from": "t2", "to": "t3"}]
    result = topological_sort(tasks, edges)
    assert result == ["t1", "t2", "t3"]


def test_topological_sort_parallel():
    """Test topological sort with parallel branches."""
    tasks = [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}]
    edges = [{"from": "t1", "to": "t2"}, {"from": "t1", "to": "t3"}]
    result = topological_sort(tasks, edges)
    assert result[0] == "t1"
    assert set(result[1:]) == {"t2", "t3"}


def test_topological_sort_cycle_detection():
    """Test cycle detection in topological sort."""
    tasks = [{"id": "t1"}, {"id": "t2"}]
    edges = [{"from": "t1", "to": "t2"}, {"from": "t2", "to": "t1"}]
    with pytest.raises(ValueError, match="Cycle detected"):
        topological_sort(tasks, edges)


def test_compute_ready_sets_sequential():
    """Test ready sets for sequential dependencies."""
    tasks = [{"id": "t1"}, {"id": "t2"}]
    edges = [{"from": "t1", "to": "t2"}]
    result = compute_ready_sets(tasks, edges)
    assert result == [{"t1"}, {"t2"}]


def test_compute_ready_sets_parallel():
    """Test ready sets for parallel execution."""
    tasks = [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}]
    edges = []
    result = compute_ready_sets(tasks, edges)
    assert result == [{"t1", "t2", "t3"}]


def test_compute_ready_sets_diamond():
    """Test ready sets for diamond-shaped DAG."""
    tasks = [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}, {"id": "t4"}]
    edges = [
        {"from": "t1", "to": "t2"},
        {"from": "t1", "to": "t3"},
        {"from": "t2", "to": "t4"},
        {"from": "t3", "to": "t4"}
    ]
    result = compute_ready_sets(tasks, edges)
    assert result[0] == {"t1"}
    assert result[1] == {"t2", "t3"}
    assert result[2] == {"t4"}
