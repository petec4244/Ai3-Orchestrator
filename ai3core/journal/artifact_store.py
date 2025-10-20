"""
Artifact Store - Stores execution artifacts with metadata
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..types import ExecutionArtifact


class ArtifactStore:
    """
    Persistent storage for execution artifacts

    Stores:
    - Raw artifacts (prompts, responses, metadata)
    - Indexed by task_id, model_id, timestamp
    - Searchable and retrievable
    """

    def __init__(self, storage_dir: str = ".ai3_artifacts"):
        """
        Initialize artifact store

        Args:
            storage_dir: Directory to store artifacts
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Index file
        self.index_file = self.storage_dir / "index.json"
        self.index: Dict[str, Any] = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load or create index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"artifacts": {}, "by_task": {}, "by_model": {}, "by_date": {}}

    def _save_index(self):
        """Persist index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def store(self, artifact: ExecutionArtifact) -> str:
        """
        Store an artifact

        Args:
            artifact: Artifact to store

        Returns:
            Artifact ID (storage key)
        """
        # Generate storage key
        timestamp_str = artifact.timestamp.strftime("%Y%m%d_%H%M%S")
        artifact_id = f"{artifact.task_id}_{artifact.model_id}_{timestamp_str}"

        # Store artifact file
        artifact_file = self.storage_dir / f"{artifact_id}.json"

        artifact_data = {
            "task_id": artifact.task_id,
            "model_id": artifact.model_id,
            "provider": artifact.provider.value,
            "prompt": artifact.prompt,
            "response": artifact.response,
            "metadata": artifact.metadata,
            "token_usage": artifact.token_usage,
            "latency_ms": artifact.latency_ms,
            "timestamp": artifact.timestamp.isoformat(),
            "success": artifact.success,
            "error": artifact.error
        }

        with open(artifact_file, 'w') as f:
            json.dump(artifact_data, f, indent=2)

        # Update index
        date_key = artifact.timestamp.strftime("%Y-%m-%d")

        self.index["artifacts"][artifact_id] = {
            "task_id": artifact.task_id,
            "model_id": artifact.model_id,
            "timestamp": artifact.timestamp.isoformat(),
            "success": artifact.success,
            "file": str(artifact_file)
        }

        # Index by task
        if artifact.task_id not in self.index["by_task"]:
            self.index["by_task"][artifact.task_id] = []
        self.index["by_task"][artifact.task_id].append(artifact_id)

        # Index by model
        if artifact.model_id not in self.index["by_model"]:
            self.index["by_model"][artifact.model_id] = []
        self.index["by_model"][artifact.model_id].append(artifact_id)

        # Index by date
        if date_key not in self.index["by_date"]:
            self.index["by_date"][date_key] = []
        self.index["by_date"][date_key].append(artifact_id)

        self._save_index()

        return artifact_id

    def retrieve(self, artifact_id: str) -> Optional[ExecutionArtifact]:
        """
        Retrieve an artifact by ID

        Args:
            artifact_id: Artifact identifier

        Returns:
            ExecutionArtifact or None if not found
        """
        if artifact_id not in self.index["artifacts"]:
            return None

        artifact_file = Path(self.index["artifacts"][artifact_id]["file"])

        if not artifact_file.exists():
            return None

        with open(artifact_file, 'r') as f:
            data = json.load(f)

        from ..types import ModelProvider

        return ExecutionArtifact(
            task_id=data["task_id"],
            model_id=data["model_id"],
            provider=ModelProvider(data["provider"]),
            prompt=data["prompt"],
            response=data["response"],
            metadata=data["metadata"],
            token_usage=data["token_usage"],
            latency_ms=data["latency_ms"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            success=data["success"],
            error=data.get("error")
        )

    def get_by_task(self, task_id: str) -> List[ExecutionArtifact]:
        """Get all artifacts for a task"""
        artifact_ids = self.index["by_task"].get(task_id, [])
        return [a for a in (self.retrieve(aid) for aid in artifact_ids) if a]

    def get_by_model(self, model_id: str) -> List[ExecutionArtifact]:
        """Get all artifacts from a specific model"""
        artifact_ids = self.index["by_model"].get(model_id, [])
        return [a for a in (self.retrieve(aid) for aid in artifact_ids) if a]

    def get_by_date(self, date: str) -> List[ExecutionArtifact]:
        """
        Get all artifacts from a specific date

        Args:
            date: Date string in YYYY-MM-DD format
        """
        artifact_ids = self.index["by_date"].get(date, [])
        return [a for a in (self.retrieve(aid) for aid in artifact_ids) if a]

    def get_recent(self, limit: int = 10) -> List[ExecutionArtifact]:
        """Get most recent artifacts"""
        all_ids = list(self.index["artifacts"].keys())
        all_ids.sort(reverse=True)  # Sort by timestamp (newest first)

        recent_ids = all_ids[:limit]
        return [a for a in (self.retrieve(aid) for aid in recent_ids) if a]

    def search(self, query: str) -> List[ExecutionArtifact]:
        """
        Search artifacts by content

        Args:
            query: Search query

        Returns:
            List of matching artifacts
        """
        matches = []

        for artifact_id in self.index["artifacts"].keys():
            artifact = self.retrieve(artifact_id)
            if not artifact:
                continue

            # Search in prompt and response
            if query.lower() in artifact.prompt.lower() or query.lower() in artifact.response.lower():
                matches.append(artifact)

        return matches

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total = len(self.index["artifacts"])
        successful = sum(1 for a in self.index["artifacts"].values() if a["success"])

        return {
            "total_artifacts": total,
            "successful": successful,
            "failed": total - successful,
            "unique_tasks": len(self.index["by_task"]),
            "unique_models": len(self.index["by_model"]),
            "storage_dir": str(self.storage_dir)
        }

    def clear(self):
        """Clear all artifacts (use with caution!)"""
        # Remove all artifact files
        for artifact_file in self.storage_dir.glob("*.json"):
            if artifact_file.name != "index.json":
                artifact_file.unlink()

        # Reset index
        self.index = {"artifacts": {}, "by_task": {}, "by_model": {}, "by_date": {}}
        self._save_index()
