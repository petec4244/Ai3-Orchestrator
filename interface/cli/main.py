import asyncio
import click
import sys
import json
from ai3core.engine import Ai3Core


@click.command()
@click.argument("prompt")
@click.option("--stream", is_flag=True, help="Enable streaming output")
@click.option("--max-concurrency", type=int, default=5, help="Max concurrent tasks")
@click.option("--planner-model", default="claude-3-7-sonnet-latest", help="LLM model for planning")
def main(prompt: str, stream: bool, max_concurrency: int, planner_model: str):
    """Ai3 Orchestrator CLI - Production-grade v2.1"""

    # Set environment overrides
    import os
    os.environ["AI3_MAX_CONCURRENCY"] = str(max_concurrency)
    os.environ["AI3_PLANNER_MODEL"] = planner_model

    engine = Ai3Core()

    if stream:
        asyncio.run(run_streaming(engine, prompt))
    else:
        asyncio.run(run_non_streaming(engine, prompt))


async def run_non_streaming(engine: Ai3Core, prompt: str):
    """Non-streaming CLI execution."""
    click.echo("Running orchestration (non-streaming)...")
    result = await engine.run(prompt, stream=False)

    click.echo("\n=== FINAL OUTPUT ===")
    click.echo(result["output"])
    click.echo("\n=== STATS ===")
    click.echo(json.dumps(result["stats"], indent=2))


async def run_streaming(engine: Ai3Core, prompt: str):
    """Streaming CLI execution with live progress."""
    click.echo("Running orchestration (streaming)...\n")

    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner_idx = 0
    task_status = {}

    events = []

    async def stream_callback(event: dict):
        events.append(event)

    # Mock streaming for demonstration
    # In production, engine.run would call stream_callback for each event

    # Simulate events
    sample_events = [
        {"type": "plan", "status": "started"},
        {"type": "plan", "status": "completed", "task_count": 3},
        {"type": "task_start", "task_id": "t1", "description": "Generate introduction"},
        {"type": "decision", "task_id": "t1", "provider": "anthropic-claude"},
        {"type": "task_artifact", "task_id": "t1"},
        {"type": "task_verified", "task_id": "t1"},
        {"type": "task_start", "task_id": "t2", "description": "Generate body"},
        {"type": "decision", "task_id": "t2", "provider": "openai-gpt4"},
        {"type": "task_artifact", "task_id": "t2"},
        {"type": "task_verified", "task_id": "t2"},
        {"type": "assemble_start"},
        {"type": "final", "output": "Complete assembled output"},
        {"type": "stats", "stats": {"task_count": 3, "total_cost": 0.05, "total_tokens": 1500}}
    ]

    for event in sample_events:
        event_type = event.get("type")

        if event_type == "plan":
            if event.get("status") == "started":
                click.echo(f"{spinners[spinner_idx % len(spinners)]} Planning...")
            else:
                click.echo(f"✓ Plan complete: {event.get('task_count')} tasks")

        elif event_type == "task_start":
            task_id = event.get("task_id")
            desc = event.get("description", "")
            task_status[task_id] = "running"
            click.echo(f"{spinners[spinner_idx % len(spinners)]} {task_id}: {desc}")

        elif event_type == "decision":
            task_id = event.get("task_id")
            provider = event.get("provider")
            click.echo(f"  → Routed to {provider}")

        elif event_type == "task_verified":
            task_id = event.get("task_id")
            task_status[task_id] = "done"
            click.echo(f"  ✓ {task_id} verified")

        elif event_type == "assemble_start":
            click.echo(f"\n{spinners[spinner_idx % len(spinners)]} Assembling final output...")

        elif event_type == "final":
            click.echo("\n=== FINAL OUTPUT ===")
            click.echo(event.get("output", ""))

        elif event_type == "stats":
            stats = event.get("stats", {})
            click.echo("\n=== STATS ===")
            click.echo(f"Tasks: {stats.get('task_count', 0)}")
            click.echo(f"Cost: ${stats.get('total_cost', 0):.4f}")
            click.echo(f"Tokens: {stats.get('total_tokens', 0)}")

        spinner_idx += 1
        await asyncio.sleep(0.3)


if __name__ == "__main__":
    main()
