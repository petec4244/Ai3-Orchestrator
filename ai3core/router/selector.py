from typing import Dict, List
from ai3core.registry.loader import load_registry


def score_provider(model_name: str, model_data: Dict, requirements: Dict, telemetry_stats: Dict) -> float:
    """Score a model based on capabilities, requirements, and telemetry."""
    score = 0.0

    # Skill/capability match
    skills = model_data.get("skills", {})
    req_cap = requirements.get("capability", "text-generation")

    # Check if required capability is in skills
    skill_score = skills.get(req_cap, 0.0)
    if skill_score > 0:
        score += 50.0 * skill_score  # Weight by skill strength
    else:
        # Fall back to text-generation as default
        score += 30.0 * skills.get("text-generation", 0.5)

    # Quality threshold - use skill score
    min_quality = requirements.get("min_quality", 0.7)
    if skill_score >= min_quality:
        score += 30.0

    # Cost efficiency (inverse relationship - lower cost = higher score)
    cost = model_data.get("cost_per_1k_tokens", 0.01)
    score += 10.0 / (cost + 0.001)

    # Telemetry feedback
    success_rate = telemetry_stats.get("success_rate", 0.8)  # Default to 0.8 if no history
    p50_latency = telemetry_stats.get("p50_latency_ms", model_data.get("avg_latency_ms", 1000.0))

    score += 20.0 * success_rate
    score -= p50_latency / 200.0  # Penalize high latency

    return score


def select_provider(task: Dict, telemetry_collector) -> str:
    """Select best model for task using weighted scoring with telemetry."""
    registry = load_registry()
    requirements = task.get("requirements", {})

    scores = {}
    models = registry.get("models", {})

    if not models:
        raise ValueError("No models available in registry")

    for model_name, model_data in models.items():
        telemetry_stats = telemetry_collector.get_provider_stats(model_name)
        scores[model_name] = score_provider(model_name, model_data, requirements, telemetry_stats)

    if not scores:
        raise ValueError("No providers available")

    chosen = max(scores, key=scores.get)
    return chosen
