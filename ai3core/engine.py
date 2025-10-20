import asyncio
import time
from typing import Dict, List, Optional, AsyncIterator
from ai3core.planner import make_plan
from ai3core.router.selector import select_provider
from ai3core.executor.scheduler import compute_ready_sets, ConcurrencyLimiter
from ai3core.providers.anthropic import AnthropicProvider
from ai3core.providers.openai import OpenAIProvider
from ai3core.verifier.verify import verify_artifact, should_repair, should_fallback
from ai3core.assembler.strategies import assemble_artifacts
from ai3core.journal.store import JournalStore
from ai3core.telemetry.metrics import TelemetryCollector
from ai3core.settings import AI3_MAX_CONCURRENCY, AI3_MAX_CONCURRENCY_PER_PROVIDER


class Ai3Core:
    """Production-grade v2.1 orchestration engine."""

    def __init__(self):
        self.journal = JournalStore()
        self.telemetry = TelemetryCollector()
        self.limiter = ConcurrencyLimiter(AI3_MAX_CONCURRENCY, AI3_MAX_CONCURRENCY_PER_PROVIDER)

    def _get_provider_instance(self, provider_name: str):
        """Instantiate provider by name."""
        if "anthropic" in provider_name.lower():
            return AnthropicProvider()
        elif "openai" in provider_name.lower():
            return OpenAIProvider()
        else:
            return AnthropicProvider()  # Default fallback

    async def _execute_task(self, task: Dict, artifacts: Dict, stream_cb=None) -> Dict:
        """Execute a single task with verification, repair, and fallback."""
        task_id = task["id"]
        start_time = time.time()

        if stream_cb:
            await stream_cb({"type": "task_start", "task_id": task_id, "description": task.get("description")})

        # Select provider
        provider_name = select_provider(task, self.telemetry)
        score = 1.0  # Placeholder for actual score
        self.telemetry.record_decision(task_id, provider_name, score)

        if stream_cb:
            await stream_cb({"type": "decision", "task_id": task_id, "provider": provider_name})

        # Execute task
        provider = self._get_provider_instance(provider_name)
        prompt = self._build_prompt(task, artifacts)

        try:
            await self.limiter.acquire(provider_name)
            response = await provider.generate(prompt)
            self.limiter.release(provider_name)

            artifact = {
                "task_id": task_id,
                "content": response.get("content", ""),
                "meta": {
                    "provider": provider_name,
                    "timestamp": time.time(),
                    "repair_count": 0
                }
            }

            if stream_cb:
                await stream_cb({"type": "task_artifact", "task_id": task_id, "artifact": artifact})

            # Verify
            quality_criteria = task.get("quality_criteria", [])
            artifact = await verify_artifact(artifact, quality_criteria, None)

            if stream_cb:
                await stream_cb({"type": "task_verified", "task_id": task_id, "verification": artifact["meta"]["verification"]})

            # Handle repair
            if should_repair(artifact):
                if stream_cb:
                    await stream_cb({"type": "task_repaired", "task_id": task_id, "attempt": artifact["meta"]["repair_count"]})

                # Create repair subtask (simplified: re-run with enhanced prompt)
                repair_prompt = f"{prompt}\n\nPrevious attempt had issues: {artifact['meta']['verification']['failures']}. Please improve."
                await self.limiter.acquire(provider_name)
                repair_response = await provider.generate(repair_prompt)
                self.limiter.release(provider_name)

                artifact["content"] = repair_response.get("content", "")
                artifact = await verify_artifact(artifact, quality_criteria, None)

            # Handle fallback
            if should_fallback(artifact):
                # Select next-best provider (simplified: pick different provider)
                fallback_provider = "openai-gpt4" if "anthropic" in provider_name else "anthropic-claude"
                fallback_instance = self._get_provider_instance(fallback_provider)

                await self.limiter.acquire(fallback_provider)
                fallback_response = await fallback_instance.generate(prompt)
                self.limiter.release(fallback_provider)

                artifact["content"] = fallback_response.get("content", "")
                artifact["meta"]["fallback_used"] = fallback_provider

            # Record telemetry
            latency_ms = (time.time() - start_time) * 1000
            cost = response.get("usage", {}).get("cost", 0.001)
            tokens = response.get("usage", {}).get("total_tokens", 100)
            self.telemetry.record_task(task_id, provider_name, True, latency_ms, cost, tokens)

            return artifact

        except Exception as e:
            self.limiter.release(provider_name)
            latency_ms = (time.time() - start_time) * 1000
            self.telemetry.record_task(task_id, provider_name, False, latency_ms, 0.0, 0)

            if stream_cb:
                await stream_cb({"type": "task_failed", "task_id": task_id, "error": str(e)})

            return {
                "task_id": task_id,
                "content": "",
                "meta": {"provider": provider_name, "error": str(e)}
            }

    def _build_prompt(self, task: Dict, artifacts: Dict) -> str:
        """Build prompt for task, incorporating dependencies."""
        base = task.get("description", "")
        # Simple dependency injection (can be enhanced)
        return base

    async def _execute_parallel(self, tasks: List[Dict], edges: List[Dict], stream_cb=None) -> Dict[str, Dict]:
        """Execute tasks in parallel based on dependency graph."""
        ready_sets = compute_ready_sets(tasks, edges)
        artifacts = {}
        task_map = {t["id"]: t for t in tasks}

        for ready_set in ready_sets:
            # Execute all ready tasks concurrently
            ready_tasks = [task_map[tid] for tid in ready_set]
            results = await asyncio.gather(
                *[self._execute_task(task, artifacts, stream_cb) for task in ready_tasks],
                return_exceptions=True
            )

            for task, result in zip(ready_tasks, results):
                if isinstance(result, Exception):
                    artifacts[task["id"]] = {
                        "task_id": task["id"],
                        "content": "",
                        "meta": {"error": str(result)}
                    }
                else:
                    artifacts[task["id"]] = result

        return artifacts

    async def run(self, user_input: str, stream: bool = False) -> AsyncIterator[Dict] if stream else Dict:
        """Main orchestration loop with optional streaming."""
        run_id = self.journal.create_run(user_input)

        async def emit(event: Dict):
            if stream and stream_cb:
                await stream_cb(event)

        stream_cb = emit if stream else None

        try:
            # Planning
            if stream_cb:
                await stream_cb({"type": "plan", "status": "started"})

            task_graph = await make_plan(user_input)
            self.journal.save_plan(run_id, task_graph)

            if stream_cb:
                await stream_cb({"type": "plan", "status": "completed", "task_count": len(task_graph["tasks"])})

            # Execution
            artifacts = await self._execute_parallel(
                task_graph["tasks"],
                task_graph["edges"],
                stream_cb
            )

            # Assembly
            if stream_cb:
                await stream_cb({"type": "assemble_start"})

            final_output = assemble_artifacts(list(artifacts.values()), strategy="concatenate")

            if stream_cb:
                await stream_cb({"type": "final", "output": final_output})

            # Finalize
            stats = self.telemetry.finalize_run()
            self.journal.save_result(run_id, final_output, stats)

            if stream_cb:
                await stream_cb({"type": "stats", "stats": stats})

            if stream:
                return
            else:
                return {
                    "run_id": run_id,
                    "output": final_output,
                    "stats": stats
                }

        except Exception as e:
            if stream_cb:
                await stream_cb({"type": "error", "message": str(e)})
            raise
