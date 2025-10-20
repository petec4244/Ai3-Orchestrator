"""
Ai3Engine - Main orchestration engine

Coordinates all modules to process prompts intelligently:
1. Plan → Task DAG
2. Route → Select best models
3. Execute → Run tasks
4. Verify → Check quality
5. Assemble → Combine results
6. Journal → Persist trace
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import RunTrace, Task, TaskStatus, ExecutionArtifact, VerificationResult, AssembledResponse
from .planner import Planner
from .registry import CapabilityRegistry
from .router import Router
from .executor import ExecutorFactory
from .verifier import Verifier
from .assembler import Assembler
from .journal import RunJournal, ArtifactStore


class Ai3Engine:
    """
    Main decision engine for multi-AI orchestration

    The Ai3Engine is Stovepipe 1 - pure business logic with no UI dependencies
    """

    def __init__(self, api_keys: Dict[str, str], config: Optional[Dict[str, Any]] = None):
        """
        Initialize the engine

        Args:
            api_keys: Dict mapping provider names to API keys
                     e.g., {"anthropic": "sk-...", "openai": "sk-...", "xai": "..."}
            config: Optional configuration overrides
        """
        self.config = config or {}

        # Initialize all modules
        self.planner = Planner()
        self.registry = CapabilityRegistry()
        self.router = Router(self.registry)
        self.executor_factory = ExecutorFactory(api_keys)
        self.verifier = Verifier()
        self.assembler = Assembler()
        self.journal = RunJournal()
        self.artifact_store = ArtifactStore()

        # Runtime state
        self.current_run_id: Optional[str] = None
        self.current_artifacts: List[ExecutionArtifact] = []
        self.current_verifications: List[VerificationResult] = []

    def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> AssembledResponse:
        """
        Main entry point: Process a prompt end-to-end

        Args:
            prompt: User's input prompt
            context: Optional additional context

        Returns:
            AssembledResponse with final result
        """
        # Generate run ID
        self.current_run_id = self._generate_run_id()
        self.current_artifacts = []
        self.current_verifications = []

        start_time = datetime.now()

        # Step 1: Plan
        print(f"[Ai3Core] Planning tasks...")
        plan = self.planner.create_plan(prompt, context)
        print(f"[Ai3Core] Created plan with {len(plan.tasks)} tasks")
        print(self.planner.visualize_plan(plan))

        # Step 2: Route
        print(f"\n[Ai3Core] Routing tasks to models...")
        assignments = self._route_tasks(plan)
        for task_id, model_id in assignments.items():
            plan.tasks[task_id].assigned_model = model_id
            print(f"  - {plan.tasks[task_id].task_type}: {model_id}")

        # Step 3: Execute
        print(f"\n[Ai3Core] Executing tasks...")
        artifacts = self._execute_tasks(plan, assignments)
        self.current_artifacts = artifacts

        # Store artifacts
        for artifact in artifacts:
            self.artifact_store.store(artifact)

        # Step 4: Verify
        print(f"\n[Ai3Core] Verifying outputs...")
        verifications = self._verify_artifacts(artifacts, plan.tasks)
        self.current_verifications = verifications

        # Handle failed verifications (repair logic)
        failed = [v for v in verifications if not v.passed and v.needs_repair]
        if failed:
            print(f"[Ai3Core] {len(failed)} tasks need repair")
            # For now, we'll proceed without repair
            # In future: retry with different models or create repair tasks

        # Step 5: Assemble
        print(f"\n[Ai3Core] Assembling final response...")
        final_response = self.assembler.assemble(
            artifacts=artifacts,
            tasks=plan.tasks,
            verifications={v.artifact_id: v for v in verifications}
        )

        # Calculate costs and latencies
        total_cost = self._calculate_total_cost(artifacts)
        total_latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Step 6: Journal
        print(f"\n[Ai3Core] Recording run trace...")
        trace = RunTrace(
            run_id=self.current_run_id,
            original_prompt=prompt,
            plan=plan,
            artifacts=artifacts,
            verifications=verifications,
            final_response=final_response,
            total_cost=total_cost,
            total_latency_ms=total_latency_ms,
            timestamp=start_time,
            metadata=context or {}
        )

        self.journal.record(trace)

        # Update telemetry
        self._update_telemetry(artifacts)

        print(f"[Ai3Core] ✓ Complete! Cost: ${total_cost:.4f}, Latency: {total_latency_ms:.0f}ms")
        print(f"[Ai3Core] Confidence: {final_response.confidence:.2f}")

        return final_response

    def _route_tasks(self, plan) -> Dict[str, str]:
        """Route all tasks to optimal models"""
        assignments = {}

        for task_id, task in plan.tasks.items():
            # Estimate context size (simplified)
            context_size = len(task.description) * 4  # Rough token estimate

            # Route task
            model_id = self.router.route_task(task, context_size)
            assignments[task_id] = model_id

        return assignments

    def _execute_tasks(self, plan, assignments: Dict[str, str]) -> List[ExecutionArtifact]:
        """Execute all tasks in dependency order"""
        artifacts = []
        completed_tasks = set()

        # Topological sort for execution order
        execution_order = self._get_execution_order(plan)

        for task_id in execution_order:
            task = plan.tasks[task_id]
            model_id = assignments[task_id]

            print(f"  Executing task {task_id[:8]}... with {model_id}")

            # Get executor
            capability = self.registry.get_capability(model_id)
            if not capability:
                print(f"    ERROR: Unknown model {model_id}")
                continue

            executor = self.executor_factory.get_executor(capability.provider)

            # Execute
            artifact = executor.execute(
                task=task,
                model_id=model_id,
                system_prompt="You are a helpful AI assistant. Provide clear, accurate responses."
            )

            artifacts.append(artifact)
            completed_tasks.add(task_id)

            # Update task status
            if artifact.success:
                task.status = TaskStatus.COMPLETED
                print(f"    ✓ Success ({artifact.token_usage.get('total', 0)} tokens, {artifact.latency_ms:.0f}ms)")
            else:
                task.status = TaskStatus.FAILED
                print(f"    ✗ Failed: {artifact.error}")

        return artifacts

    def _verify_artifacts(self, artifacts: List[ExecutionArtifact],
                         tasks: Dict[str, Task]) -> List[VerificationResult]:
        """Verify all artifacts"""
        verifications = []

        for artifact in artifacts:
            task = tasks.get(artifact.task_id)
            if not task:
                continue

            verification = self.verifier.verify(artifact, task)
            verifications.append(verification)

            status = "✓ PASS" if verification.passed else "✗ FAIL"
            print(f"    {artifact.task_id[:8]}: {status} (score: {verification.score:.2f})")

        return verifications

    def _get_execution_order(self, plan) -> List[str]:
        """
        Get task execution order using topological sort

        Returns:
            List of task IDs in execution order
        """
        # Simple topological sort
        visited = set()
        order = []

        def visit(task_id: str):
            if task_id in visited:
                return

            task = plan.tasks[task_id]

            # Visit dependencies first
            for dep_id in task.dependencies:
                if dep_id in plan.tasks:
                    visit(dep_id)

            visited.add(task_id)
            order.append(task_id)

        # Start from root tasks
        for root_id in plan.root_task_ids:
            visit(root_id)

        # Visit any remaining tasks (shouldn't happen with proper DAG)
        for task_id in plan.tasks:
            if task_id not in visited:
                visit(task_id)

        return order

    def _calculate_total_cost(self, artifacts: List[ExecutionArtifact]) -> float:
        """Calculate total cost from all artifacts"""
        total_cost = 0.0

        for artifact in artifacts:
            capability = self.registry.get_capability(artifact.model_id)
            if not capability:
                continue

            total_tokens = artifact.token_usage.get("total", 0)
            cost = (total_tokens / 1000.0) * capability.cost_per_1k_tokens
            total_cost += cost

        return total_cost

    def _update_telemetry(self, artifacts: List[ExecutionArtifact]):
        """Update registry telemetry from artifacts"""
        for artifact in artifacts:
            capability = self.registry.get_capability(artifact.model_id)
            if not capability:
                continue

            total_tokens = artifact.token_usage.get("total", 0)
            cost = (total_tokens / 1000.0) * capability.cost_per_1k_tokens

            self.registry.update_telemetry(
                model_id=artifact.model_id,
                success=artifact.success,
                latency_ms=artifact.latency_ms,
                tokens_used=total_tokens,
                cost=cost
            )

    def _generate_run_id(self) -> str:
        """Generate unique run ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "registry": self.registry.get_live_metrics("claude-3-7-sonnet-20250219"),
            "journal": self.journal.get_stats(),
            "artifacts": self.artifact_store.get_stats(),
            "router": self.router.get_routing_stats()
        }

    def get_last_trace(self) -> Optional[RunTrace]:
        """Get the most recent run trace"""
        if not self.current_run_id:
            # Get from journal
            recent = self.journal.get_recent(limit=1)
            return recent[0] if recent else None

        return self.journal.retrieve(self.current_run_id)

    def replay_run(self, run_id: str) -> Optional[RunTrace]:
        """
        Replay a previous run for debugging

        Args:
            run_id: Run identifier

        Returns:
            RunTrace or None if not found
        """
        return self.journal.retrieve(run_id)

    def set_routing_override(self, task_type: str, model_id: str):
        """Set a routing override for a task type"""
        self.router.set_override(task_type, model_id)

    def clear_routing_override(self, task_type: str):
        """Clear a routing override"""
        self.router.remove_override(task_type)
