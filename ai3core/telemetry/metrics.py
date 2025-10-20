import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from ai3core.settings import TELEMETRY_DIR


class TelemetryCollector:
    """Collect and persist runtime metrics for router feedback."""

    def __init__(self):
        self.metrics_file = TELEMETRY_DIR / "metrics.json"
        self.current_run = {
            "tasks": [],
            "decisions": [],
            "total_cost": 0.0,
            "total_tokens": 0
        }
        self.historical = self.load_historical()

    def load_historical(self) -> Dict:
        """Load historical metrics from disk."""
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                return json.load(f)
        return {"provider_stats": {}}

    def save_historical(self):
        """Persist historical metrics to disk."""
        with open(self.metrics_file, "w") as f:
            json.dump(self.historical, f, indent=2)

    def record_task(self, task_id: str, provider: str, success: bool, latency_ms: float, cost: float, tokens: int):
        """Record task execution metrics."""
        self.current_run["tasks"].append({
            "task_id": task_id,
            "provider": provider,
            "success": success,
            "latency_ms": latency_ms,
            "cost": cost,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.current_run["total_cost"] += cost
        self.current_run["total_tokens"] += tokens

        # Update historical provider stats
        if provider not in self.historical["provider_stats"]:
            self.historical["provider_stats"][provider] = {
                "total_runs": 0,
                "successes": 0,
                "total_latency_ms": 0.0,
                "total_cost": 0.0,
                "total_tokens": 0
            }

        stats = self.historical["provider_stats"][provider]
        stats["total_runs"] += 1
        if success:
            stats["successes"] += 1
        stats["total_latency_ms"] += latency_ms
        stats["total_cost"] += cost
        stats["total_tokens"] += tokens

    def record_decision(self, task_id: str, chosen_provider: str, score: float):
        """Record routing decision."""
        self.current_run["decisions"].append({
            "task_id": task_id,
            "chosen_provider": chosen_provider,
            "score": score
        })

    def get_provider_stats(self, provider: str) -> Dict:
        """Get rolling stats for a provider."""
        if provider not in self.historical["provider_stats"]:
            return {
                "success_rate": 0.5,
                "p50_latency_ms": 1000.0,
                "avg_cost": 0.001
            }

        stats = self.historical["provider_stats"][provider]
        success_rate = stats["successes"] / max(stats["total_runs"], 1)
        p50_latency = stats["total_latency_ms"] / max(stats["total_runs"], 1)
        avg_cost = stats["total_cost"] / max(stats["total_runs"], 1)

        return {
            "success_rate": success_rate,
            "p50_latency_ms": p50_latency,
            "avg_cost": avg_cost
        }

    def finalize_run(self) -> Dict:
        """Finalize current run and save metrics."""
        self.save_historical()
        run_summary = {
            "task_count": len(self.current_run["tasks"]),
            "decision_count": len(self.current_run["decisions"]),
            "total_cost": self.current_run["total_cost"],
            "total_tokens": self.current_run["total_tokens"]
        }
        return run_summary
