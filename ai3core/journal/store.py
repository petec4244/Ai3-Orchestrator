import json
import time
from pathlib import Path
from typing import Dict, Optional
from ai3core.settings import JOURNAL_DIR


class JournalStore:
    """Persist run traces and events for streaming playback."""

    def __init__(self):
        self.journal_dir = JOURNAL_DIR

    def create_run(self, user_input: str) -> str:
        """Create a new run directory and return run_id."""
        run_id = f"run_{int(time.time() * 1000)}"
        run_path = self.journal_dir / run_id
        run_path.mkdir(exist_ok=True)

        with open(run_path / "input.txt", "w") as f:
            f.write(user_input)

        return run_id

    def save_plan(self, run_id: str, task_graph: Dict):
        """Save task graph plan."""
        run_path = self.journal_dir / run_id
        with open(run_path / "plan.json", "w") as f:
            json.dump(task_graph, f, indent=2)

    def save_result(self, run_id: str, output: str, stats: Dict):
        """Save final output and stats."""
        run_path = self.journal_dir / run_id

        with open(run_path / "output.txt", "w") as f:
            f.write(output)

        with open(run_path / "stats.json", "w") as f:
            json.dump(stats, f, indent=2)

    def append_event(self, run_id: str, event: Dict):
        """Append streaming event to trace log."""
        run_path = self.journal_dir / run_id
        trace_file = run_path / "trace.jsonl"

        with open(trace_file, "a") as f:
            f.write(json.dumps(event) + "\n")
