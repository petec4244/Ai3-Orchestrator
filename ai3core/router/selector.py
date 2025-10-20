from typing import Dict, List
from ai3core.registry.loader import load_registry


def score_provider(provider: Dict, requirements: Dict, telemetry_stats: Dict) -> float:
    """Score a provider based on capabilities, requirements, and telemetry."""
    score = 0.0

    # Capability match
    caps = provider.get("capabilities", {})
    req_cap = requirements.get("capability", "text-generation")
    if req_cap in caps.get("primary", []) or req_cap in caps.get("secondary", []):
        score += 50.0

    # Quality threshold
    quality = caps.get("quality_score", 0.5)
    min_quality = requirements.get("min_quality", 0.7)
    if quality >= min_quality:
        score += 30.0 * quality

    # Cost efficiency
    cost = provider.get("cost_per_1k_tokens", 0.01)
    score += 10.0 / (cost + 0.001)

    # Telemetry feedback
    success_rate = telemetry_stats.get("success_rate", 0.5)
    p50_latency = telemetry_stats.get("p50_latency_ms", 1000.0)

    score += 20.0 * success_rate
    score -= p50_latency / 100.0  # Penalize high latency

    return score


def select_provider(task: Dict, telemetry_collector) -> str:
    """Select best provider for task using weighted scoring with telemetry."""
    registry = load_registry()
    requirements = task.get("requirements", {})

    scores = {}
    for provider_name, provider_data in registry["providers"].items():
        telemetry_stats = telemetry_collector.get_provider_stats(provider_name)
        scores[provider_name] = score_provider(provider_data, requirements, telemetry_stats)

    if not scores:
        raise ValueError("No providers available")

    chosen = max(scores, key=scores.get)
    return chosen
