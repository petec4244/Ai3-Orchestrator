#!/usr/bin/env python3
"""
Test script for Grok/XAI integration

This verifies that Grok models are properly integrated into ai3core
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))


def test_xai_models_in_registry():
    """Test that Grok models are loaded in the registry"""
    print("Testing Grok models in Capability Registry...")
    from ai3core.registry import CapabilityRegistry

    registry = CapabilityRegistry()

    # Check if Grok models are registered
    grok_models = [
        "xai-grok4",
        "xai-grok4-fast",
        "xai-grok4-fast-reasoning",
        "xai-grok3"
    ]

    for model_id in grok_models:
        capability = registry.get_capability(model_id)
        assert capability is not None, f"Model {model_id} should be in registry"
        print(f"  [OK] {model_id}: {capability.model_id}")
        print(f"    - Context window: {capability.context_window}")
        print(f"    - Cost per 1K tokens: ${capability.cost_per_1k_tokens}")
        print(f"    - Skills: {list(capability.skills.keys())}")

    print()


def test_xai_adapter_models():
    """Test that XAI adapter recognizes Grok models"""
    print("Testing XAI Adapter model validation...")
    from ai3core.executor.xai_adapter import XAIAdapter

    adapter = XAIAdapter("test-key")

    # Test valid models
    valid_models = [
        "grok-4",
        "grok-4-fast",
        "grok-4-fast-reasoning",
        "grok-4-fast-non-reasoning",
        "grok-3",
        "grok-2-latest",
        "grok-2"
    ]

    for model in valid_models:
        assert adapter.validate_model(model), f"{model} should be valid"
        print(f"  [OK] {model} is valid")

    # Test invalid model
    assert not adapter.validate_model("grok-1"), "grok-1 should be invalid"
    print(f"  [OK] Invalid models correctly rejected")

    print()


def test_xai_provider():
    """Test that XAI provider can be instantiated"""
    print("Testing XAI Provider...")
    from ai3core.providers.xai import XAIProvider

    # Test default instantiation
    provider = XAIProvider()
    assert provider.model == "grok-4-fast", "Default model should be grok-4-fast"
    assert provider.api_base == "https://api.x.ai/v1", "API base should be correct"
    print(f"  [OK] Default provider created: {provider.model}")

    # Test custom model
    provider = XAIProvider(model="grok-4", max_tokens=8192, temperature=0.5)
    assert provider.model == "grok-4"
    assert provider.max_tokens == 8192
    assert provider.temperature == 0.5
    print(f"  [OK] Custom provider created: {provider.model}")

    # Test cost calculation
    cost_grok4 = provider._calculate_cost(1000, 1000)
    assert cost_grok4 > 0, "Cost should be calculated"
    print(f"  [OK] Cost calculation: ${cost_grok4:.6f} for 1K input/output tokens")

    provider_fast = XAIProvider(model="grok-4-fast")
    cost_grok4_fast = provider_fast._calculate_cost(1000, 1000)
    assert cost_grok4_fast < cost_grok4, "Grok 4 Fast should be cheaper"
    print(f"  [OK] Grok 4 Fast cost: ${cost_grok4_fast:.6f} (cheaper than Grok 4)")

    print()


def test_executor_factory_xai():
    """Test that ExecutorFactory can create XAI executors"""
    print("Testing ExecutorFactory XAI integration...")
    from ai3core.executor.executor_factory import ExecutorFactory
    from ai3core.types import ModelProvider

    factory = ExecutorFactory({
        "anthropic": "test-key",
        "openai": "test-key",
        "xai": "test-xai-key"
    })

    # Get XAI executor
    executor = factory.get_executor(ModelProvider.XAI)
    assert executor is not None, "Should create XAI executor"
    assert executor.provider == ModelProvider.XAI
    print(f"  [OK] XAI executor created: {executor.__class__.__name__}")

    # Verify it's cached
    executor2 = factory.get_executor(ModelProvider.XAI)
    assert executor is executor2, "Should return cached instance"
    print(f"  [OK] Executor caching works")

    print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("Grok/XAI Integration Test Suite")
    print("=" * 60)
    print()

    try:
        test_xai_models_in_registry()
        test_xai_adapter_models()
        test_xai_provider()
        test_executor_factory_xai()

        print("=" * 60)
        print("ALL TESTS PASSED [SUCCESS]")
        print("=" * 60)
        print()
        print("Grok is now fully integrated into ai3core!")
        print()
        print("Available Grok models:")
        print("  - grok-4: Premium model with advanced reasoning")
        print("  - grok-4-fast: Fast, cost-effective model with 2M context")
        print("  - grok-4-fast-reasoning: Optimized for reasoning tasks")
        print("  - grok-3: Previous generation model")
        print()
        print("To use Grok, set your XAI_API_KEY environment variable.")

    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
