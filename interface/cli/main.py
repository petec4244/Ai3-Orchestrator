#!/usr/bin/env python3
"""
Ai3 CLI - Command-line interface for Ai3Core decision engine

Usage:
    python -m interface.cli.main "your prompt here"
    python -m interface.cli.main --stats
    python -m interface.cli.main --history
    python -m interface.cli.main --replay RUN_ID
"""

import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai3core import Ai3Engine


def load_api_keys():
    """Load API keys from environment"""
    # Try to load from .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Also try backend/.env for backwards compatibility
    backend_env = Path.cwd() / "backend" / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)

    api_keys = {}

    # Load API keys
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")

    if os.getenv("OPENAI_API_KEY"):
        api_keys["openai"] = os.getenv("OPENAI_API_KEY")

    if os.getenv("XAI_API_KEY"):
        api_keys["xai"] = os.getenv("XAI_API_KEY")

    if not api_keys:
        print("ERROR: No API keys found in environment")
        print("Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or XAI_API_KEY")
        sys.exit(1)

    return api_keys


def cmd_process(args, engine):
    """Process a prompt"""
    prompt = args.prompt

    if not prompt:
        print("ERROR: No prompt provided")
        sys.exit(1)

    print("="*80)
    print("AI3 ORCHESTRATOR - Decision Engine")
    print("="*80)
    print(f"Prompt: {prompt}\n")

    try:
        response = engine.process(prompt)

        print("\n" + "="*80)
        print("FINAL RESPONSE")
        print("="*80)
        print(response.content)
        print("\n" + "="*80)
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Assembly Method: {response.assembly_method}")
        print(f"Sources: {len(response.source_artifacts)}")
        print("="*80)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_stats(args, engine):
    """Show engine statistics"""
    stats = engine.get_stats()

    print("="*80)
    print("AI3 ENGINE STATISTICS")
    print("="*80)

    print("\n📊 Journal:")
    for key, value in stats["journal"].items():
        print(f"  {key}: {value}")

    print("\n📦 Artifacts:")
    for key, value in stats["artifacts"].items():
        print(f"  {key}: {value}")

    print("\n🧭 Router:")
    for key, value in stats["router"].items():
        print(f"  {key}: {value}")

    print("="*80)


def cmd_history(args, engine):
    """Show recent run history"""
    traces = engine.journal.get_recent(limit=args.limit)

    print("="*80)
    print(f"RECENT RUNS (last {args.limit})")
    print("="*80)

    for trace in traces:
        print(f"\nRun ID: {trace.run_id}")
        print(f"Timestamp: {trace.timestamp}")
        print(f"Prompt: {trace.original_prompt[:80]}...")
        print(f"Tasks: {len(trace.plan.tasks)}")
        print(f"Cost: ${trace.total_cost:.4f}")
        print(f"Latency: {trace.total_latency_ms:.0f}ms")
        print(f"Confidence: {trace.final_response.confidence:.2f}")
        print("-"*80)


def cmd_replay(args, engine):
    """Replay a previous run"""
    trace = engine.replay_run(args.run_id)

    if not trace:
        print(f"ERROR: Run {args.run_id} not found")
        sys.exit(1)

    print("="*80)
    print(f"REPLAY RUN: {trace.run_id}")
    print("="*80)

    print(f"\nTimestamp: {trace.timestamp}")
    print(f"Prompt: {trace.original_prompt}\n")

    print("Tasks:")
    for task_id, task in trace.plan.tasks.items():
        print(f"  - [{task.task_type}] {task.description[:60]}...")
        print(f"    Assigned: {task.assigned_model}")
        print(f"    Status: {task.status.value}")

    print("\nArtifacts:")
    for artifact in trace.artifacts:
        status = "✓" if artifact.success else "✗"
        print(f"  {status} {artifact.model_id}: {artifact.token_usage.get('total', 0)} tokens, {artifact.latency_ms:.0f}ms")

    print("\nVerifications:")
    for verification in trace.verifications:
        status = "✓ PASS" if verification.passed else "✗ FAIL"
        print(f"  {status} {verification.artifact_id}: {verification.score:.2f}")

    print(f"\n{'='*80}")
    print("FINAL RESPONSE")
    print("="*80)
    print(trace.final_response.content)
    print("="*80)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Ai3 Orchestrator - Intelligent Multi-AI Decision Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to process"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show engine statistics"
    )

    parser.add_argument(
        "--history",
        action="store_true",
        help="Show recent run history"
    )

    parser.add_argument(
        "--replay",
        metavar="RUN_ID",
        help="Replay a previous run"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of history items to show (default: 10)"
    )

    args = parser.parse_args()

    # Load API keys
    api_keys = load_api_keys()

    # Initialize engine
    print("Initializing Ai3 Engine...")
    engine = Ai3Engine(api_keys=api_keys)

    # Route to appropriate command
    if args.stats:
        cmd_stats(args, engine)
    elif args.history:
        cmd_history(args, engine)
    elif args.replay:
        args.run_id = args.replay
        cmd_replay(args, engine)
    elif args.prompt:
        cmd_process(args, engine)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
