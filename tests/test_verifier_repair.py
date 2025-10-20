import pytest
import asyncio
from ai3core.verifier.verify import verify_artifact, should_repair, should_fallback
from ai3core.settings import AI3_VERIFY, AI3_REPAIR_LIMIT


@pytest.mark.asyncio
async def test_verify_artifact_passes():
    """Test verification passes for valid content."""
    artifact = {
        "content": "This is a well-formed piece of content with sufficient length and coherence.",
        "meta": {}
    }
    quality_criteria = ["non-empty", "min-length-100"]

    result = await verify_artifact(artifact, quality_criteria, None)
    assert result["meta"]["verification"]["status"] == "passed"


@pytest.mark.asyncio
async def test_verify_artifact_fails():
    """Test verification fails for invalid content."""
    artifact = {
        "content": "Short",
        "meta": {}
    }
    quality_criteria = ["min-length-100"]

    result = await verify_artifact(artifact, quality_criteria, None)
    assert result["meta"]["verification"]["status"] == "failed"
    assert len(result["meta"]["verification"]["failures"]) > 0


@pytest.mark.asyncio
async def test_verify_artifact_repair_attempted():
    """Test verification marks repair attempt."""
    artifact = {
        "content": "",
        "meta": {}
    }
    quality_criteria = ["non-empty"]

    result = await verify_artifact(artifact, quality_criteria, None)
    assert result["meta"]["verification"]["repair_attempted"] is True
    assert result["meta"]["repair_count"] == 1


def test_should_repair_true():
    """Test should_repair returns True when repair needed."""
    artifact = {
        "meta": {
            "verification": {
                "status": "failed",
                "repair_attempted": True
            },
            "repair_count": 1
        }
    }
    assert should_repair(artifact) is True


def test_should_fallback_true():
    """Test should_fallback returns True when fallback recommended."""
    artifact = {
        "meta": {
            "verification": {
                "status": "failed",
                "fallback_recommended": True
            }
        }
    }
    assert should_fallback(artifact) is True


def test_should_fallback_false():
    """Test should_fallback returns False when not recommended."""
    artifact = {
        "meta": {
            "verification": {
                "status": "passed"
            }
        }
    }
    assert should_fallback(artifact) is False
