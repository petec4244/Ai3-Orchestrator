from typing import Dict, List, Set
import asyncio


def topological_sort(tasks: List[Dict], edges: List[Dict]) -> List[str]:
    """Return task IDs in topological order."""
    # Build adjacency list
    graph = {t["id"]: [] for t in tasks}
    in_degree = {t["id"]: 0 for t in tasks}

    for edge in edges:
        graph[edge["from"]].append(edge["to"])
        in_degree[edge["to"]] += 1

    # Kahn's algorithm
    queue = [tid for tid, deg in in_degree.items() if deg == 0]
    result = []

    while queue:
        queue.sort()  # Deterministic ordering
        node = queue.pop(0)
        result.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(tasks):
        raise ValueError("Cycle detected in task graph")

    return result


def compute_ready_sets(tasks: List[Dict], edges: List[Dict]) -> List[Set[str]]:
    """Return list of sets, each containing task IDs that can run in parallel."""
    # Build dependency map
    dependencies = {t["id"]: set() for t in tasks}
    for edge in edges:
        dependencies[edge["to"]].add(edge["from"])

    ready_sets = []
    completed = set()
    task_ids = {t["id"] for t in tasks}

    while len(completed) < len(tasks):
        ready = set()
        for tid in task_ids - completed:
            if dependencies[tid].issubset(completed):
                ready.add(tid)

        if not ready:
            raise ValueError("No ready tasks found; possible cycle")

        ready_sets.append(ready)
        completed.update(ready)

    return ready_sets


class ConcurrencyLimiter:
    """Global and per-provider concurrency control."""

    def __init__(self, max_global: int, max_per_provider: int):
        self.max_global = max_global
        self.max_per_provider = max_per_provider
        self.global_sem = asyncio.Semaphore(max_global)
        self.provider_sems = {}

    def get_semaphore(self, provider: str) -> asyncio.Semaphore:
        """Get or create semaphore for provider."""
        if provider not in self.provider_sems:
            self.provider_sems[provider] = asyncio.Semaphore(self.max_per_provider)
        return self.provider_sems[provider]

    async def acquire(self, provider: str):
        """Acquire both global and provider-specific semaphores."""
        await self.global_sem.acquire()
        await self.get_semaphore(provider).acquire()

    def release(self, provider: str):
        """Release both global and provider-specific semaphores."""
        self.global_sem.release()
        self.get_semaphore(provider).release()
