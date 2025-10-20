"""
Run Journal - Records complete execution traces
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..types import RunTrace, TaskGraph, ExecutionArtifact, VerificationResult, AssembledResponse


class RunJournal:
    """
    Journal for complete execution traces

    Records:
    - Original prompt
    - Generated plan (task DAG)
    - All artifacts produced
    - Verification results
    - Final assembled response
    - Costs, latencies, routing decisions
    - Full audit trail for replay and debugging
    """

    def __init__(self, journal_dir: str = ".ai3_journal"):
        """
        Initialize run journal

        Args:
            journal_dir: Directory to store run traces
        """
        self.journal_dir = Path(journal_dir)
        self.journal_dir.mkdir(parents=True, exist_ok=True)

        # Index file
        self.index_file = self.journal_dir / "runs_index.json"
        self.index: Dict[str, Any] = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load or create index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"runs": {}, "by_date": {}}

    def _save_index(self):
        """Persist index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def record(self, trace: RunTrace) -> str:
        """
        Record a complete run trace

        Args:
            trace: RunTrace to record

        Returns:
            Run ID
        """
        # Store run file
        run_file = self.journal_dir / f"{trace.run_id}.json"

        run_data = self._serialize_trace(trace)

        with open(run_file, 'w') as f:
            json.dump(run_data, f, indent=2)

        # Update index
        date_key = trace.timestamp.strftime("%Y-%m-%d")

        self.index["runs"][trace.run_id] = {
            "timestamp": trace.timestamp.isoformat(),
            "prompt": trace.original_prompt[:100] + "..." if len(trace.original_prompt) > 100 else trace.original_prompt,
            "num_tasks": len(trace.plan.tasks),
            "num_artifacts": len(trace.artifacts),
            "total_cost": trace.total_cost,
            "total_latency_ms": trace.total_latency_ms,
            "file": str(run_file)
        }

        # Index by date
        if date_key not in self.index["by_date"]:
            self.index["by_date"][date_key] = []
        self.index["by_date"][date_key].append(trace.run_id)

        self._save_index()

        return trace.run_id

    def retrieve(self, run_id: str) -> Optional[RunTrace]:
        """
        Retrieve a run trace

        Args:
            run_id: Run identifier

        Returns:
            RunTrace or None if not found
        """
        if run_id not in self.index["runs"]:
            return None

        run_file = Path(self.index["runs"][run_id]["file"])

        if not run_file.exists():
            return None

        with open(run_file, 'r') as f:
            data = json.load(f)

        return self._deserialize_trace(data)

    def get_recent(self, limit: int = 10) -> List[RunTrace]:
        """Get most recent runs"""
        all_ids = list(self.index["runs"].keys())
        all_ids.sort(reverse=True)  # Sort by timestamp (newest first)

        recent_ids = all_ids[:limit]
        return [r for r in (self.retrieve(rid) for rid in recent_ids) if r]

    def get_by_date(self, date: str) -> List[RunTrace]:
        """
        Get all runs from a specific date

        Args:
            date: Date string in YYYY-MM-DD format
        """
        run_ids = self.index["by_date"].get(date, [])
        return [r for r in (self.retrieve(rid) for rid in run_ids) if r]

    def get_stats(self) -> Dict[str, Any]:
        """Get journal statistics"""
        total_runs = len(self.index["runs"])

        if total_runs == 0:
            return {
                "total_runs": 0,
                "total_cost": 0.0,
                "avg_latency_ms": 0.0,
                "journal_dir": str(self.journal_dir)
            }

        total_cost = sum(r["total_cost"] for r in self.index["runs"].values())
        avg_latency = sum(r["total_latency_ms"] for r in self.index["runs"].values()) / total_runs

        return {
            "total_runs": total_runs,
            "total_cost": total_cost,
            "avg_cost_per_run": total_cost / total_runs,
            "avg_latency_ms": avg_latency,
            "journal_dir": str(self.journal_dir)
        }

    def _serialize_trace(self, trace: RunTrace) -> Dict[str, Any]:
        """Serialize RunTrace to JSON-compatible dict"""
        from ..types import ModelProvider

        return {
            "run_id": trace.run_id,
            "original_prompt": trace.original_prompt,
            "plan": {
                "tasks": {
                    task_id: {
                        "id": task.id,
                        "description": task.description,
                        "task_type": task.task_type,
                        "dependencies": task.dependencies,
                        "success_criteria": task.success_criteria,
                        "context": task.context,
                        "status": task.status.value,
                        "assigned_model": task.assigned_model,
                        "priority": task.priority
                    }
                    for task_id, task in trace.plan.tasks.items()
                },
                "root_task_ids": trace.plan.root_task_ids,
                "metadata": trace.plan.metadata
            },
            "artifacts": [
                {
                    "task_id": a.task_id,
                    "model_id": a.model_id,
                    "provider": a.provider.value,
                    "prompt": a.prompt,
                    "response": a.response,
                    "metadata": a.metadata,
                    "token_usage": a.token_usage,
                    "latency_ms": a.latency_ms,
                    "timestamp": a.timestamp.isoformat(),
                    "success": a.success,
                    "error": a.error
                }
                for a in trace.artifacts
            ],
            "verifications": [
                {
                    "artifact_id": v.artifact_id,
                    "passed": v.passed,
                    "score": v.score,
                    "criteria_results": v.criteria_results,
                    "feedback": v.feedback,
                    "needs_repair": v.needs_repair,
                    "suggested_fixes": v.suggested_fixes
                }
                for v in trace.verifications
            ],
            "final_response": {
                "content": trace.final_response.content,
                "source_artifacts": trace.final_response.source_artifacts,
                "confidence": trace.final_response.confidence,
                "assembly_method": trace.final_response.assembly_method,
                "metadata": trace.final_response.metadata
            },
            "total_cost": trace.total_cost,
            "total_latency_ms": trace.total_latency_ms,
            "timestamp": trace.timestamp.isoformat(),
            "metadata": trace.metadata
        }

    def _deserialize_trace(self, data: Dict[str, Any]) -> RunTrace:
        """Deserialize RunTrace from JSON dict"""
        from ..types import (Task, TaskStatus, TaskGraph, ExecutionArtifact,
                            ModelProvider, VerificationResult, AssembledResponse)

        # Deserialize plan
        tasks = {}
        for task_id, task_data in data["plan"]["tasks"].items():
            tasks[task_id] = Task(
                id=task_data["id"],
                description=task_data["description"],
                task_type=task_data["task_type"],
                dependencies=task_data["dependencies"],
                success_criteria=task_data["success_criteria"],
                context=task_data["context"],
                status=TaskStatus(task_data["status"]),
                assigned_model=task_data.get("assigned_model"),
                priority=task_data.get("priority", 0)
            )

        plan = TaskGraph(
            tasks=tasks,
            root_task_ids=data["plan"]["root_task_ids"],
            metadata=data["plan"]["metadata"]
        )

        # Deserialize artifacts
        artifacts = [
            ExecutionArtifact(
                task_id=a["task_id"],
                model_id=a["model_id"],
                provider=ModelProvider(a["provider"]),
                prompt=a["prompt"],
                response=a["response"],
                metadata=a["metadata"],
                token_usage=a["token_usage"],
                latency_ms=a["latency_ms"],
                timestamp=datetime.fromisoformat(a["timestamp"]),
                success=a["success"],
                error=a.get("error")
            )
            for a in data["artifacts"]
        ]

        # Deserialize verifications
        verifications = [
            VerificationResult(
                artifact_id=v["artifact_id"],
                passed=v["passed"],
                score=v["score"],
                criteria_results=v["criteria_results"],
                feedback=v["feedback"],
                needs_repair=v["needs_repair"],
                suggested_fixes=v["suggested_fixes"]
            )
            for v in data["verifications"]
        ]

        # Deserialize final response
        final_response = AssembledResponse(
            content=data["final_response"]["content"],
            source_artifacts=data["final_response"]["source_artifacts"],
            confidence=data["final_response"]["confidence"],
            assembly_method=data["final_response"]["assembly_method"],
            metadata=data["final_response"]["metadata"]
        )

        return RunTrace(
            run_id=data["run_id"],
            original_prompt=data["original_prompt"],
            plan=plan,
            artifacts=artifacts,
            verifications=verifications,
            final_response=final_response,
            total_cost=data["total_cost"],
            total_latency_ms=data["total_latency_ms"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )
