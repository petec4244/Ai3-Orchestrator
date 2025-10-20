#!/usr/bin/env python3
"""
Quick test script for Ai3Core components

This tests the core modules without requiring API keys
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def test_planner():
    """Test the Planner module"""
    print("Testing Planner...")
    from ai3core.planner import Planner

    planner = Planner()

    # Test simple task
    plan = planner.create_plan("Write a hello world program")
    assert len(plan.tasks) >= 1, "Should create at least one task"
    print(f"  ✓ Simple task: {len(plan.tasks)} task(s)")

    # Test complex task
    plan = planner.create_plan("""
    1. Create a database schema for users
    2. Write API endpoints for CRUD operations
    3. Add authentication
    4. Write tests
    """)
    assert len(plan.tasks) >= 4, "Should create multiple tasks"
    print(f"  ✓ Complex task: {len(plan.tasks)} task(s)")

    print(planner.visualize_plan(plan))
    print()


def test_registry():
    """Test the Capability Registry"""
    print("Testing Capability Registry...")
    from ai3core.registry import CapabilityRegistry

    registry = CapabilityRegistry()

    # Test model loading
    models = registry.get_all_models()
    assert len(models) > 0, "Should load models from config"
    print(f"  ✓ Loaded {len(models)} models")

    # Test capability lookup
    claude = registry.get_capability("claude-3-7-sonnet-20250219")
    assert claude is not None, "Should find Claude model"
    assert claude.skills["coding"] > 0.9, "Claude should have high coding skill"
    print(f"  ✓ Claude coding skill: {claude.skills['coding']}")

    # Test skill ranking
    rankings = registry.rank_models_for_task("coding")
    assert len(rankings) > 0, "Should rank models"
    print(f"  ✓ Top model for coding: {rankings[0][0]} (score: {rankings[0][1]:.2f})")
    print()


def test_router():
    """Test the Router module"""
    print("Testing Router...")
    from ai3core.router import Router
    from ai3core.registry import CapabilityRegistry
    from ai3core.types import Task

    registry = CapabilityRegistry()
    router = Router(registry)

    # Create test task
    task = Task(
        id="test1",
        description="Write a Python function",
        task_type="coding",
        dependencies=[],
        success_criteria=["Should have valid Python syntax"]
    )

    # Test routing
    model_id = router.route_task(task)
    assert model_id in registry.get_all_models(), "Should select valid model"
    print(f"  ✓ Routed coding task to: {model_id}")

    # Test explanation
    explanation = router.get_routing_explanation(task, model_id)
    print(f"  ✓ Routing explanation generated ({len(explanation)} chars)")
    print()


def test_verifier():
    """Test the Verifier module"""
    print("Testing Verifier...")
    from ai3core.verifier import Verifier
    from ai3core.types import ExecutionArtifact, Task, ModelProvider
    from datetime import datetime

    verifier = Verifier()

    task = Task(
        id="test1",
        description="Write a hello world function",
        task_type="coding",
        dependencies=[],
        success_criteria=["Should contain a function definition", "Should print hello world"]
    )

    # Create successful artifact
    artifact = ExecutionArtifact(
        task_id="test1",
        model_id="claude-3-7-sonnet-20250219",
        provider=ModelProvider.ANTHROPIC,
        prompt="Write a hello world function",
        response="def hello_world():\n    print('Hello, World!')\n    return True",
        metadata={},
        token_usage={"input": 10, "output": 20, "total": 30},
        latency_ms=1500.0,
        timestamp=datetime.now(),
        success=True
    )

    result = verifier.verify(artifact, task)
    print(f"  ✓ Verification score: {result.score:.2f}")
    print(f"  ✓ Passed: {result.passed}")
    print(f"  ✓ Feedback: {result.feedback}")
    print()


def test_assembler():
    """Test the Assembler module"""
    print("Testing Assembler...")
    from ai3core.assembler import Assembler
    from ai3core.types import ExecutionArtifact, Task, ModelProvider
    from datetime import datetime

    assembler = Assembler()

    # Create test artifacts
    artifacts = [
        ExecutionArtifact(
            task_id="task1",
            model_id="claude-3-7-sonnet-20250219",
            provider=ModelProvider.ANTHROPIC,
            prompt="Explain quantum computing",
            response="Quantum computing uses quantum mechanics principles...",
            metadata={},
            token_usage={"input": 10, "output": 50, "total": 60},
            latency_ms=2000.0,
            timestamp=datetime.now(),
            success=True
        ),
        ExecutionArtifact(
            task_id="task2",
            model_id="gpt-4o",
            provider=ModelProvider.OPENAI,
            prompt="List quantum computing applications",
            response="1. Cryptography\n2. Drug discovery\n3. Optimization",
            metadata={},
            token_usage={"input": 8, "output": 30, "total": 38},
            latency_ms=1500.0,
            timestamp=datetime.now(),
            success=True
        )
    ]

    tasks = {
        "task1": Task(id="task1", description="Explain quantum computing", task_type="general", dependencies=[], success_criteria=[]),
        "task2": Task(id="task2", description="List applications", task_type="general", dependencies=[], success_criteria=[])
    }

    response = assembler.assemble(artifacts, tasks)
    print(f"  ✓ Assembled {len(response.source_artifacts)} artifacts")
    print(f"  ✓ Confidence: {response.confidence:.2f}")
    print(f"  ✓ Method: {response.assembly_method}")
    print(f"  ✓ Response length: {len(response.content)} chars")
    print()


def test_journal():
    """Test the Journal system"""
    print("Testing Journal & Artifact Store...")
    from ai3core.journal import RunJournal, ArtifactStore
    from ai3core.types import ExecutionArtifact, ModelProvider
    from datetime import datetime
    import tempfile
    import shutil

    # Use temp directory
    temp_dir = tempfile.mkdtemp()

    try:
        artifact_store = ArtifactStore(storage_dir=f"{temp_dir}/artifacts")

        # Create test artifact
        artifact = ExecutionArtifact(
            task_id="test1",
            model_id="claude-3-7-sonnet-20250219",
            provider=ModelProvider.ANTHROPIC,
            prompt="Test prompt",
            response="Test response",
            metadata={},
            token_usage={"input": 10, "output": 20, "total": 30},
            latency_ms=1000.0,
            timestamp=datetime.now(),
            success=True
        )

        # Store and retrieve
        artifact_id = artifact_store.store(artifact)
        retrieved = artifact_store.retrieve(artifact_id)

        assert retrieved is not None, "Should retrieve artifact"
        assert retrieved.response == artifact.response, "Response should match"
        print(f"  ✓ Artifact store: Stored and retrieved artifact")

        stats = artifact_store.get_stats()
        print(f"  ✓ Total artifacts: {stats['total_artifacts']}")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

    print()


def main():
    """Run all tests"""
    print("="*80)
    print("AI3CORE COMPONENT TESTS")
    print("="*80)
    print()

    try:
        test_planner()
        test_registry()
        test_router()
        test_verifier()
        test_assembler()
        test_journal()

        print("="*80)
        print("✓ ALL TESTS PASSED")
        print("="*80)
        print()
        print("Ai3Core is ready to use!")
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: python -m interface.cli.main 'your prompt here'")
        print()

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
