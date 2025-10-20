"""
Anthropic (Claude) adapter
"""

import time
from typing import Optional, Dict, Any
from anthropic import Anthropic, APIError
from .base import BaseExecutor
from ..types import ExecutionArtifact, ModelProvider, Task


class AnthropicAdapter(BaseExecutor):
    """Adapter for Anthropic Claude models"""

    VALID_MODELS = [
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    def __init__(self, api_key: str):
        """Initialize Anthropic adapter"""
        super().__init__(api_key, ModelProvider.ANTHROPIC)
        self.client = Anthropic(api_key=api_key)

    def execute(self, task: Task, model_id: str, system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                **kwargs) -> ExecutionArtifact:
        """
        Execute task using Claude

        Args:
            task: Task to execute
            model_id: Claude model to use
            system_prompt: Optional system prompt
            max_tokens: Max output tokens (default 4096)
            temperature: Sampling temperature (default 0.7)
            **kwargs: Additional Anthropic-specific params

        Returns:
            ExecutionArtifact with results
        """
        start_time = time.time()

        try:
            # Build prompt
            user_prompt = self._build_prompt(task, None)  # Anthropic uses separate system param

            # Prepare request
            request_params = {
                "model": model_id,
                "max_tokens": max_tokens or self.default_max_tokens,
                "temperature": temperature or self.default_temperature,
                "messages": [{"role": "user", "content": user_prompt}]
            }

            if system_prompt:
                request_params["system"] = system_prompt

            # Merge additional kwargs
            request_params.update(kwargs)

            # Make API call
            response = self.client.messages.create(**request_params)

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            response_text = response.content[0].text if response.content else ""

            # Extract token usage
            token_usage = {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens
            }

            metadata = {
                "model": response.model,
                "stop_reason": response.stop_reason,
                "request_id": response.id
            }

            return self._create_artifact(
                task=task,
                model_id=model_id,
                prompt=user_prompt,
                response=response_text,
                token_usage=token_usage,
                latency_ms=latency_ms,
                success=True,
                metadata=metadata
            )

        except APIError as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Anthropic API error: {str(e)}"

            return self._create_artifact(
                task=task,
                model_id=model_id,
                prompt=self._build_prompt(task, system_prompt),
                response="",
                token_usage={"input": 0, "output": 0, "total": 0},
                latency_ms=latency_ms,
                success=False,
                error=error_msg
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Unexpected error: {str(e)}"

            return self._create_artifact(
                task=task,
                model_id=model_id,
                prompt=self._build_prompt(task, system_prompt),
                response="",
                token_usage={"input": 0, "output": 0, "total": 0},
                latency_ms=latency_ms,
                success=False,
                error=error_msg
            )

    def validate_model(self, model_id: str) -> bool:
        """Check if model_id is a valid Claude model"""
        return model_id in self.VALID_MODELS
