"""
Planner - Decomposes prompts into task DAGs
"""

import json
import uuid
import re
from typing import List, Dict, Any, Optional
from ..types import Task, TaskGraph, TaskStatus


class Planner:
    """
    Converts user prompts into structured task plans (DAGs)

    The planner analyzes the prompt and creates a graph of tasks with:
    - Clear descriptions
    - Task types (for routing)
    - Dependencies between tasks
    - Success criteria for verification
    """

    # Task type keywords for classification
    TASK_KEYWORDS = {
        "coding": ["code", "implement", "function", "class", "debug", "refactor", "api", "script", "program"],
        "reasoning": ["analyze", "solve", "calculate", "prove", "logic", "deduce", "infer", "reason"],
        "creative": ["write", "create", "story", "poem", "generate", "brainstorm", "design", "imagine"],
        "professional_writing": ["document", "report", "specification", "proposal", "memo", "email", "letter"],
        "summarization": ["summarize", "summary", "condense", "brief", "overview", "tldr", "digest"],
        "data_analysis": ["analyze data", "visualize", "statistics", "metrics", "dashboard", "chart", "graph"],
        "document_processing": ["parse", "extract", "read document", "process pdf", "ocr"],
        "multimodal": ["image", "picture", "photo", "video", "audio", "vision"],
        "research": ["research", "find", "search", "investigate", "explore", "discover"],
        "planning": ["plan", "strategy", "roadmap", "schedule", "organize"],
        "general": []  # fallback
    }

    # Patterns that indicate multi-step tasks
    MULTI_STEP_PATTERNS = [
        r"(?:first|then|next|finally|after that)",
        r"(?:step \d+|phase \d+|stage \d+)",
        r"(?:\d+\.\s+|\d+\)\s+)",  # numbered lists
        r"(?:and then|followed by)",
    ]

    def __init__(self, planning_model: Optional[str] = None):
        """
        Initialize the planner

        Args:
            planning_model: Optional specific model to use for planning tasks
        """
        self.planning_model = planning_model

    def create_plan(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> TaskGraph:
        """
        Main entry point: Convert a prompt into a TaskGraph

        Args:
            prompt: User's input prompt
            context: Optional additional context

        Returns:
            TaskGraph with tasks and dependencies
        """
        # Analyze if this is a simple or complex task
        is_complex = self._is_complex_task(prompt)

        if is_complex:
            tasks = self._decompose_complex_task(prompt, context or {})
        else:
            tasks = self._create_simple_task(prompt, context or {})

        # Build task dictionary and identify roots
        task_dict = {task.id: task for task in tasks}
        root_ids = [t.id for t in tasks if not t.dependencies]

        return TaskGraph(
            tasks=task_dict,
            root_task_ids=root_ids,
            metadata={
                "original_prompt": prompt,
                "is_complex": is_complex,
                "num_tasks": len(tasks)
            }
        )

    def _is_complex_task(self, prompt: str) -> bool:
        """Determine if prompt requires task decomposition"""
        # Check for multi-step indicators
        for pattern in self.MULTI_STEP_PATTERNS:
            if re.search(pattern, prompt.lower()):
                return True

        # Check for multiple sentence structure
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        if len(sentences) > 3:
            return True

        # Check for conjunctions indicating multiple parts
        conjunction_count = len(re.findall(r'\b(and|then|also|additionally|furthermore)\b', prompt.lower()))
        if conjunction_count > 2:
            return True

        return False

    def _create_simple_task(self, prompt: str, context: Dict[str, Any]) -> List[Task]:
        """Create a single task for simple prompts"""
        task_type = self._classify_task(prompt)
        task_id = str(uuid.uuid4())[:8]

        criteria = self._extract_success_criteria(prompt)

        return [Task(
            id=task_id,
            description=prompt,
            task_type=task_type,
            dependencies=[],
            success_criteria=criteria,
            context=context,
            status=TaskStatus.PENDING
        )]

    def _decompose_complex_task(self, prompt: str, context: Dict[str, Any]) -> List[Task]:
        """Break down complex prompts into multiple tasks"""
        tasks = []

        # Try to identify discrete steps
        # Pattern 1: Numbered lists
        numbered_steps = re.findall(r'(?:^|\n)\s*\d+[\.)]\s+([^\n]+)', prompt)

        if numbered_steps:
            tasks = self._create_tasks_from_steps(numbered_steps, context)
        else:
            # Pattern 2: Split by conjunctions and sentence structure
            tasks = self._create_tasks_from_sentences(prompt, context)

        # If we still only have one task, check for implicit steps
        if len(tasks) <= 1:
            tasks = self._infer_implicit_steps(prompt, context)

        return tasks

    def _create_tasks_from_steps(self, steps: List[str], context: Dict[str, Any]) -> List[Task]:
        """Create tasks from explicit numbered steps"""
        tasks = []
        previous_task_id = None

        for idx, step in enumerate(steps):
            task_id = str(uuid.uuid4())[:8]
            task_type = self._classify_task(step)

            dependencies = [previous_task_id] if previous_task_id else []

            task = Task(
                id=task_id,
                description=step.strip(),
                task_type=task_type,
                dependencies=dependencies,
                success_criteria=self._extract_success_criteria(step),
                context=context,
                status=TaskStatus.PENDING,
                priority=idx
            )
            tasks.append(task)
            previous_task_id = task_id

        return tasks

    def _create_tasks_from_sentences(self, prompt: str, context: Dict[str, Any]) -> List[Task]:
        """Create tasks by analyzing sentence structure"""
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', prompt) if s.strip()]

        if len(sentences) <= 1:
            return self._create_simple_task(prompt, context)

        tasks = []
        previous_task_id = None

        for idx, sentence in enumerate(sentences):
            # Skip very short sentences (likely fragments)
            if len(sentence.split()) < 3:
                continue

            task_id = str(uuid.uuid4())[:8]
            task_type = self._classify_task(sentence)

            # Check if sentence indicates dependency
            has_dependency = any(word in sentence.lower() for word in ['then', 'after', 'next', 'finally'])
            dependencies = [previous_task_id] if (previous_task_id and has_dependency) else []

            task = Task(
                id=task_id,
                description=sentence,
                task_type=task_type,
                dependencies=dependencies,
                success_criteria=self._extract_success_criteria(sentence),
                context=context,
                status=TaskStatus.PENDING,
                priority=idx
            )
            tasks.append(task)
            previous_task_id = task_id

        return tasks if tasks else self._create_simple_task(prompt, context)

    def _infer_implicit_steps(self, prompt: str, context: Dict[str, Any]) -> List[Task]:
        """Infer logical steps from prompt even if not explicitly listed"""
        # Common patterns: "Create X that does Y" -> ["Create X structure", "Implement Y functionality"]

        # For now, return as single task if we can't infer steps
        # This can be enhanced with LLM-based planning in future
        return self._create_simple_task(prompt, context)

    def _classify_task(self, text: str) -> str:
        """Classify task type based on keywords"""
        text_lower = text.lower()
        scores = {}

        for task_type, keywords in self.TASK_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[task_type] = score

        # Return type with highest score, default to general
        max_score = max(scores.values())
        if max_score == 0:
            return "general"

        return max(scores.items(), key=lambda x: x[1])[0]

    def _extract_success_criteria(self, text: str) -> List[str]:
        """Extract or infer success criteria from task description"""
        criteria = []

        # Look for explicit criteria patterns
        if "should" in text.lower():
            criteria.append("Meets specified requirements")

        if any(word in text.lower() for word in ["test", "verify", "check"]):
            criteria.append("Passes validation checks")

        if any(word in text.lower() for word in ["error", "bug", "fix"]):
            criteria.append("Resolves identified issues")

        # Default criteria
        if not criteria:
            criteria = ["Completes task successfully", "Produces valid output"]

        return criteria

    def visualize_plan(self, plan: TaskGraph) -> str:
        """Generate a text visualization of the plan"""
        lines = ["Task Plan:", "=" * 50]

        def print_task(task: Task, indent: int = 0):
            prefix = "  " * indent
            deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            lines.append(f"{prefix}- [{task.task_type}] {task.description}{deps}")
            lines.append(f"{prefix}  Criteria: {', '.join(task.success_criteria)}")

        # Print tasks in dependency order
        printed = set()

        def print_recursive(task_id: str, indent: int = 0):
            if task_id in printed:
                return
            task = plan.tasks[task_id]
            # Print dependencies first
            for dep_id in task.dependencies:
                print_recursive(dep_id, indent)
            print_task(task, indent)
            printed.add(task_id)

        for root_id in plan.root_task_ids:
            print_recursive(root_id)

        # Print any remaining tasks (shouldn't happen with proper DAG)
        for task_id in plan.tasks:
            if task_id not in printed:
                print_recursive(task_id)

        return "\n".join(lines)
