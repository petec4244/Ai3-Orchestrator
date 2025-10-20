"""
Base executor interface for AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from ..types import ExecutionArtifact, ModelProvider, Task


class BaseExecutor(ABC):
    """
    Abstract base class for AI provider executors

    All adapters must implement this interface to ensure uniform behavior
    """

    def __init__(self, api_key: str, provider: ModelProvider):
        """
        Initialize the executor

        Args:
            api_key: API key for the provider
            provider: ModelProvider enum value
        """
        self.api_key = api_key
        self.provider = provider
        self.default_max_tokens = 4096
        self.default_temperature = 0.7

    @abstractmethod
    def execute(self, task: Task, model_id: str, system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                **kwargs) -> ExecutionArtifact:
        """
        Execute a task using the specified model

        Args:
            task: Task to execute
            model_id: Specific model to use
            system_prompt: Optional system prompt
            max_tokens: Max output tokens
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters

        Returns:
            ExecutionArtifact with results

        Raises:
            Exception: If execution fails
        """
        pass

    @abstractmethod
    def validate_model(self, model_id: str) -> bool:
        """
        Check if model_id is valid for this provider

        Args:
            model_id: Model identifier

        Returns:
            True if valid, False otherwise
        """
        pass

    def _create_artifact(self, task: Task, model_id: str, prompt: str, response: str,
                        token_usage: Dict[str, int], latency_ms: float,
                        success: bool = True, error: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> ExecutionArtifact:
        """
        Helper to create ExecutionArtifact

        Args:
            task: The task that was executed
            model_id: Model used
            prompt: Full prompt sent
            response: Response received
            token_usage: Dict with input/output/total tokens
            latency_ms: Execution time in milliseconds
            success: Whether execution succeeded
            error: Error message if failed
            metadata: Additional metadata

        Returns:
            ExecutionArtifact
        """
        return ExecutionArtifact(
            task_id=task.id,
            model_id=model_id,
            provider=self.provider,
            prompt=prompt,
            response=response,
            metadata=metadata or {},
            token_usage=token_usage,
            latency_ms=latency_ms,
            timestamp=datetime.now(),
            success=success,
            error=error
        )

    def _build_prompt(self, task: Task, system_prompt: Optional[str] = None) -> str:
        """
        Build full prompt from task

        Args:
            task: Task to build prompt for
            system_prompt: Optional system prompt

        Returns:
            Complete prompt string
        """
        parts = []

        if system_prompt:
            parts.append(f"System: {system_prompt}")

        parts.append(f"Task: {task.description}")

        if task.context:
            parts.append(f"Context: {task.context}")

        if task.success_criteria:
            parts.append(f"Success criteria: {', '.join(task.success_criteria)}")

        return "\n\n".join(parts)
