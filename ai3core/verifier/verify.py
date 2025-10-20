from typing import Dict, Any, Optional
from ai3core.settings import AI3_VERIFY, AI3_REPAIR_LIMIT


async def verify_artifact(artifact: Dict, quality_criteria: list, executor_fn) -> Dict:
    """
    Verify artifact against quality_criteria.
    If verification fails and repair is enabled, create ONE repair subtask.
    If repair fails, return fallback recommendation.
    """
    if not AI3_VERIFY:
        artifact["meta"]["verification"] = {"status": "skipped"}
        return artifact

    # Simple heuristic verification
    content = artifact.get("content", "")
    failures = []

    for criterion in quality_criteria:
        if criterion.lower() == "non-empty" and not content.strip():
            failures.append("Content is empty")
        elif criterion.lower() == "min-length-100" and len(content) < 100:
            failures.append("Content too short (< 100 chars)")
        elif criterion.lower() == "coherent" and len(content.split()) < 10:
            failures.append("Content lacks coherence (< 10 words)")

    if not failures:
        artifact["meta"]["verification"] = {
            "status": "passed",
            "criteria": quality_criteria,
            "timestamp": artifact["meta"].get("timestamp")
        }
        return artifact

    # Verification failed
    artifact["meta"]["verification"] = {
        "status": "failed",
        "criteria": quality_criteria,
        "failures": failures
    }

    # Attempt repair if within limit
    repair_count = artifact["meta"].get("repair_count", 0)
    if repair_count < AI3_REPAIR_LIMIT:
        artifact["meta"]["repair_count"] = repair_count + 1
        artifact["meta"]["verification"]["repair_attempted"] = True
        # Caller will handle repair subtask generation
        return artifact

    # Exceeded repair limit; suggest fallback
    artifact["meta"]["verification"]["fallback_recommended"] = True
    return artifact


def should_repair(artifact: Dict) -> bool:
    """Check if artifact needs repair."""
    verification = artifact.get("meta", {}).get("verification", {})
    return (
        verification.get("status") == "failed" and
        verification.get("repair_attempted") and
        artifact["meta"].get("repair_count", 0) <= AI3_REPAIR_LIMIT
    )


def should_fallback(artifact: Dict) -> bool:
    """Check if artifact needs fallback to next-best model."""
    verification = artifact.get("meta", {}).get("verification", {})
    return verification.get("fallback_recommended", False)
