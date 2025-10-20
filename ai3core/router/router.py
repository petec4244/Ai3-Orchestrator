"""
Router - Selects optimal AI model for each task using scoring functions
"""

from typing import Dict, List, Optional, Tuple
from ..types import Task, ModelCapability
from ..registry import CapabilityRegistry


class Router:
    """
    Intelligent routing engine that selects the best model for each task

    Uses a weighted scoring function considering:
    - Task-specific skill match
    - Current performance metrics (latency, error rate)
    - Cost efficiency
    - Context window requirements
    - Feature requirements (vision, streaming, etc.)
    - User preferences and overrides
    """

    # Default weights for scoring function
    DEFAULT_WEIGHTS = {
        "skill_match": 0.50,      # How well model's skills match task type
        "performance": 0.20,       # Current error rate and latency
        "cost": 0.15,             # Cost efficiency
        "context_fit": 0.10,      # Context window adequacy
        "features": 0.05          # Feature support bonus
    }

    def __init__(self, registry: CapabilityRegistry, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the router

        Args:
            registry: Capability registry to query
            weights: Optional custom weights for scoring function
        """
        self.registry = registry
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.user_overrides: Dict[str, str] = {}  # task_type -> model_id overrides
        self.fallback_models = ["gpt-4o", "claude-3-7-sonnet-20250219"]

    def route_task(self, task: Task, context_size: int = 0,
                   required_features: Optional[Dict[str, bool]] = None) -> str:
        """
        Select the best model for a task

        Args:
            task: Task to route
            context_size: Estimated context size in tokens
            required_features: Required features (vision, streaming, etc.)

        Returns:
            Selected model_id
        """
        # Check for user override
        if task.task_type in self.user_overrides:
            override_model = self.user_overrides[task.task_type]
            if override_model in self.registry.capabilities:
                return override_model

        # Score all available models
        scores = self._score_models(task, context_size, required_features)

        if not scores:
            # Fallback to default model
            return self._get_fallback_model(context_size, required_features)

        # Return highest scoring model
        best_model, best_score = scores[0]
        return best_model

    def route_tasks(self, tasks: List[Task], context_sizes: Optional[Dict[str, int]] = None) -> Dict[str, str]:
        """
        Route multiple tasks in batch

        Args:
            tasks: List of tasks to route
            context_sizes: Optional context size per task_id

        Returns:
            Dict mapping task_id -> model_id
        """
        assignments = {}
        context_sizes = context_sizes or {}

        for task in tasks:
            context_size = context_sizes.get(task.id, 0)
            model_id = self.route_task(task, context_size)
            assignments[task.id] = model_id

        return assignments

    def _score_models(self, task: Task, context_size: int,
                      required_features: Optional[Dict[str, bool]]) -> List[Tuple[str, float]]:
        """
        Score all models for a task using weighted scoring function

        Returns:
            List of (model_id, score) sorted by score descending
        """
        scores = []

        for model_id, capability in self.registry.capabilities.items():
            # Filter by required features
            if required_features:
                if required_features.get("vision") and not capability.supports_vision:
                    continue
                if required_features.get("streaming") and not capability.supports_streaming:
                    continue
                if required_features.get("function_calling") and not capability.supports_function_calling:
                    continue

            # Filter by context window
            if context_size > 0 and context_size > capability.context_window:
                continue

            # Calculate weighted score
            score = self._calculate_score(task, capability, context_size, required_features)
            scores.append((model_id, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def _calculate_score(self, task: Task, capability: ModelCapability,
                        context_size: int, required_features: Optional[Dict[str, bool]]) -> float:
        """
        Calculate weighted score for a model on a task

        Score components:
        1. Skill match: How well model's skills align with task type
        2. Performance: Based on error rate and latency
        3. Cost: Lower cost = higher score
        4. Context fit: How well context window fits the need
        5. Features: Bonus for supporting required features
        """
        # 1. Skill match score (0-1)
        skill_score = capability.skills.get(task.task_type, 0.5)

        # 2. Performance score (0-1)
        # Lower error rate and latency = higher score
        error_score = 1.0 - capability.error_rate  # 0.95 if 5% error rate
        latency_score = max(0.0, 1.0 - (capability.avg_latency_ms / 10000))  # Normalize to 10s max
        performance_score = (error_score * 0.7) + (latency_score * 0.3)

        # 3. Cost score (0-1)
        # Normalize cost - cheaper is better
        # Assuming max cost of $0.01 per 1k tokens
        max_cost = 0.01
        cost_score = 1.0 - min(capability.cost_per_1k_tokens / max_cost, 1.0)

        # 4. Context fit score (0-1)
        if context_size == 0:
            context_score = 1.0  # No context requirement
        else:
            utilization = context_size / capability.context_window
            # Prefer models where context is 20-80% of window (sweet spot)
            if utilization < 0.2:
                context_score = 0.8  # Overkill
            elif utilization < 0.8:
                context_score = 1.0  # Perfect fit
            else:
                context_score = 0.6  # Near limit

        # 5. Features score (0-1)
        feature_score = 1.0
        if required_features:
            supported_count = sum([
                capability.supports_vision if required_features.get("vision") else True,
                capability.supports_streaming if required_features.get("streaming") else True,
                capability.supports_function_calling if required_features.get("function_calling") else True
            ])
            required_count = sum(required_features.values())
            feature_score = supported_count / max(required_count, 1)

        # Weighted combination
        final_score = (
            self.weights["skill_match"] * skill_score +
            self.weights["performance"] * performance_score +
            self.weights["cost"] * cost_score +
            self.weights["context_fit"] * context_score +
            self.weights["features"] * feature_score
        )

        return final_score

    def _get_fallback_model(self, context_size: int,
                           required_features: Optional[Dict[str, bool]]) -> str:
        """Get a fallback model if routing fails"""
        for model_id in self.fallback_models:
            if model_id not in self.registry.capabilities:
                continue

            capability = self.registry.capabilities[model_id]

            # Check context window
            if context_size > 0 and context_size > capability.context_window:
                continue

            # Check features
            if required_features:
                if required_features.get("vision") and not capability.supports_vision:
                    continue
                if required_features.get("streaming") and not capability.supports_streaming:
                    continue

            return model_id

        # Last resort: return first available model
        return list(self.registry.capabilities.keys())[0]

    def set_override(self, task_type: str, model_id: str):
        """
        Set a user override for a task type

        Args:
            task_type: Type of task
            model_id: Model to always use for this task type
        """
        if model_id in self.registry.capabilities:
            self.user_overrides[task_type] = model_id

    def remove_override(self, task_type: str):
        """Remove a user override"""
        if task_type in self.user_overrides:
            del self.user_overrides[task_type]

    def get_routing_explanation(self, task: Task, model_id: str,
                                context_size: int = 0) -> str:
        """
        Generate human-readable explanation of routing decision

        Args:
            task: The task
            model_id: The selected model
            context_size: Context size used

        Returns:
            Explanation string
        """
        capability = self.registry.capabilities.get(model_id)
        if not capability:
            return f"Unknown model: {model_id}"

        lines = [
            f"Task: {task.description[:60]}...",
            f"Type: {task.task_type}",
            f"Selected Model: {model_id}",
            f"Provider: {capability.provider.value}",
            "",
            "Reasons:",
        ]

        # Skill match
        skill_score = capability.skills.get(task.task_type, 0.5)
        lines.append(f"  - Skill match: {skill_score:.2f} / 1.0")

        # Performance
        live_metrics = self.registry.get_live_metrics(model_id)
        if live_metrics:
            lines.append(f"  - Error rate: {capability.error_rate:.1%}")
            lines.append(f"  - Avg latency: {capability.avg_latency_ms:.0f}ms")

        # Cost
        lines.append(f"  - Cost: ${capability.cost_per_1k_tokens:.4f} per 1k tokens")

        # Context
        if context_size > 0:
            lines.append(f"  - Context: {context_size:,} / {capability.context_window:,} tokens")

        # Features
        features = []
        if capability.supports_vision:
            features.append("vision")
        if capability.supports_streaming:
            features.append("streaming")
        if capability.supports_function_calling:
            features.append("function calling")

        if features:
            lines.append(f"  - Features: {', '.join(features)}")

        return "\n".join(lines)

    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update scoring weights

        Args:
            new_weights: New weight values (should sum to ~1.0)
        """
        # Validate weights
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            # Normalize if close enough
            new_weights = {k: v / total for k, v in new_weights.items()}

        self.weights.update(new_weights)

    def get_routing_stats(self) -> Dict:
        """Get statistics about routing decisions"""
        return {
            "available_models": len(self.registry.capabilities),
            "active_overrides": len(self.user_overrides),
            "current_weights": self.weights.copy(),
            "fallback_models": self.fallback_models.copy()
        }
