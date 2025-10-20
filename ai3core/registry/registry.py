"""
Capability Registry - Manages model capabilities and performance metrics
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..types import ModelCapability, ModelProvider


class CapabilityRegistry:
    """
    Central registry of AI model capabilities and performance metrics

    Maintains:
    - Static skill matrices (from config)
    - Rolling performance metrics (latency, error rates, cost)
    - Context window and feature support info
    - User overrides and customizations
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the registry

        Args:
            config_path: Path to capabilities.json, defaults to bundled config
        """
        if config_path is None:
            config_path = Path(__file__).parent / "capabilities.json"

        self.config_path = Path(config_path)
        self.capabilities: Dict[str, ModelCapability] = {}
        self.telemetry: Dict[str, Dict] = {}  # Rolling metrics per model
        self.telemetry_window_hours = 24

        self._load_capabilities()

    def _load_capabilities(self):
        """Load capabilities from JSON config"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)

            self.telemetry_window_hours = data.get("telemetry_window_hours", 24)

            for model_id, config in data.get("models", {}).items():
                provider_str = config.get("provider", "openai")
                provider = ModelProvider(provider_str)

                capability = ModelCapability(
                    model_id=model_id,
                    provider=provider,
                    skills=config.get("skills", {}),
                    context_window=config.get("context_window", 8192),
                    cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.001),
                    avg_latency_ms=config.get("avg_latency_ms", 2000),
                    error_rate=config.get("error_rate", 0.05),
                    supports_streaming=config.get("supports_streaming", True),
                    supports_vision=config.get("supports_vision", False),
                    supports_function_calling=config.get("supports_function_calling", False),
                    max_output_tokens=config.get("max_output_tokens", 4096),
                    metadata={"notes": config.get("notes", "")}
                )
                self.capabilities[model_id] = capability

                # Initialize telemetry tracking
                self.telemetry[model_id] = {
                    "recent_calls": [],
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "success_count": 0,
                    "error_count": 0
                }

        except Exception as e:
            raise ValueError(f"Failed to load capabilities from {self.config_path}: {e}")

    def get_capability(self, model_id: str) -> Optional[ModelCapability]:
        """Get capability info for a specific model"""
        return self.capabilities.get(model_id)

    def get_all_models(self) -> List[str]:
        """Get list of all registered model IDs"""
        return list(self.capabilities.keys())

    def get_models_by_provider(self, provider: ModelProvider) -> List[str]:
        """Get all models from a specific provider"""
        return [
            model_id for model_id, cap in self.capabilities.items()
            if cap.provider == provider
        ]

    def get_skill_score(self, model_id: str, skill: str) -> float:
        """
        Get proficiency score for a model on a specific skill

        Args:
            model_id: Model identifier
            skill: Skill name (e.g., 'coding', 'reasoning')

        Returns:
            Proficiency score 0-1, or 0.5 if unknown
        """
        capability = self.capabilities.get(model_id)
        if not capability:
            return 0.5

        return capability.skills.get(skill, 0.5)

    def update_telemetry(self, model_id: str, success: bool, latency_ms: float,
                        tokens_used: int, cost: float):
        """
        Update rolling telemetry metrics

        Args:
            model_id: Model that was called
            success: Whether call succeeded
            latency_ms: Latency in milliseconds
            tokens_used: Total tokens consumed
            cost: Cost in dollars
        """
        if model_id not in self.telemetry:
            self.telemetry[model_id] = {
                "recent_calls": [],
                "total_tokens": 0,
                "total_cost": 0.0,
                "success_count": 0,
                "error_count": 0
            }

        telem = self.telemetry[model_id]

        # Add to recent calls
        telem["recent_calls"].append({
            "timestamp": datetime.now(),
            "success": success,
            "latency_ms": latency_ms,
            "tokens": tokens_used,
            "cost": cost
        })

        # Update totals
        telem["total_tokens"] += tokens_used
        telem["total_cost"] += cost

        if success:
            telem["success_count"] += 1
        else:
            telem["error_count"] += 1

        # Clean old telemetry outside window
        cutoff = datetime.now() - timedelta(hours=self.telemetry_window_hours)
        telem["recent_calls"] = [
            call for call in telem["recent_calls"]
            if call["timestamp"] > cutoff
        ]

        # Update capability metrics based on recent data
        self._update_capability_metrics(model_id)

    def _update_capability_metrics(self, model_id: str):
        """Recalculate capability metrics from telemetry"""
        if model_id not in self.capabilities or model_id not in self.telemetry:
            return

        telem = self.telemetry[model_id]
        recent = telem["recent_calls"]

        if not recent:
            return

        capability = self.capabilities[model_id]

        # Update average latency
        avg_latency = sum(c["latency_ms"] for c in recent) / len(recent)
        capability.avg_latency_ms = avg_latency

        # Update error rate
        total = telem["success_count"] + telem["error_count"]
        if total > 0:
            capability.error_rate = telem["error_count"] / total

    def get_live_metrics(self, model_id: str) -> Dict:
        """Get current telemetry metrics for a model"""
        if model_id not in self.telemetry:
            return {}

        telem = self.telemetry[model_id]
        recent = telem["recent_calls"]

        if not recent:
            return {
                "calls_in_window": 0,
                "avg_latency_ms": 0,
                "error_rate": 0,
                "total_cost": 0
            }

        return {
            "calls_in_window": len(recent),
            "avg_latency_ms": sum(c["latency_ms"] for c in recent) / len(recent),
            "success_rate": telem["success_count"] / (telem["success_count"] + telem["error_count"]),
            "error_rate": telem["error_count"] / (telem["success_count"] + telem["error_count"]),
            "total_tokens": telem["total_tokens"],
            "total_cost": telem["total_cost"]
        }

    def rank_models_for_task(self, task_type: str, required_features: Optional[Dict[str, bool]] = None) -> List[tuple]:
        """
        Rank all models by suitability for a task type

        Args:
            task_type: Type of task (coding, reasoning, etc.)
            required_features: Optional feature requirements (vision, streaming, etc.)

        Returns:
            List of (model_id, score) tuples, sorted by score descending
        """
        scores = []

        for model_id, capability in self.capabilities.items():
            # Base skill score
            skill_score = capability.skills.get(task_type, 0.5)

            # Check required features
            if required_features:
                if required_features.get("vision") and not capability.supports_vision:
                    continue
                if required_features.get("streaming") and not capability.supports_streaming:
                    continue
                if required_features.get("function_calling") and not capability.supports_function_calling:
                    continue

            # Adjust for current performance
            error_penalty = capability.error_rate * 0.2  # Up to -0.2 for high error rate
            final_score = skill_score - error_penalty

            scores.append((model_id, final_score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def save_capabilities(self):
        """Persist current capabilities to JSON file"""
        data = {
            "models": {},
            "telemetry_window_hours": self.telemetry_window_hours,
            "last_updated": datetime.now().isoformat()
        }

        for model_id, capability in self.capabilities.items():
            data["models"][model_id] = {
                "provider": capability.provider.value,
                "skills": capability.skills,
                "context_window": capability.context_window,
                "cost_per_1k_tokens": capability.cost_per_1k_tokens,
                "avg_latency_ms": capability.avg_latency_ms,
                "error_rate": capability.error_rate,
                "supports_streaming": capability.supports_streaming,
                "supports_vision": capability.supports_vision,
                "supports_function_calling": capability.supports_function_calling,
                "max_output_tokens": capability.max_output_tokens,
                "notes": capability.metadata.get("notes", "")
            }

        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_model(self, capability: ModelCapability):
        """Add or update a model in the registry"""
        self.capabilities[capability.model_id] = capability
        if capability.model_id not in self.telemetry:
            self.telemetry[capability.model_id] = {
                "recent_calls": [],
                "total_tokens": 0,
                "total_cost": 0.0,
                "success_count": 0,
                "error_count": 0
            }

    def remove_model(self, model_id: str):
        """Remove a model from the registry"""
        if model_id in self.capabilities:
            del self.capabilities[model_id]
        if model_id in self.telemetry:
            del self.telemetry[model_id]
