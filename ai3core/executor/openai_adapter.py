"""
OpenAI (GPT) adapter
"""

import time
from typing import Optional, Dict, Any
from openai import OpenAI, APIError
from .base import BaseExecutor
from ..types import ExecutionArtifact, ModelProvider, Task


class OpenAIAdapter(BaseExecutor):
    """Adapter for OpenAI GPT models"""

    VALID_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]

    def __init__(self, api_key: str):
        """Initialize OpenAI adapter"""
        super().__init__(api_key, ModelProvider.OPENAI)
        self.client = OpenAI(api_key=api_key)

    def execute(self, task: Task, model_id: str, system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                **kwargs) -> ExecutionArtifact:
        """
        Execute task using GPT

        Args:
            task: Task to execute
            model_id: GPT model to use
            system_prompt: Optional system prompt
            max_tokens: Max output tokens (default 4096)
            temperature: Sampling temperature (default 0.7)
            **kwargs: Additional OpenAI-specific params

        Returns:
            ExecutionArtifact with results
        """
        start_time = time.time()

        try:
            # Build messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            user_prompt = self._build_prompt(task, None)
            messages.append({"role": "user", "content": user_prompt})

            # Prepare request
            request_params = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature or self.default_temperature,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Merge additional kwargs
            request_params.update(kwargs)

            # Make API call
            response = self.client.chat.completions.create(**request_params)

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            response_text = response.choices[0].message.content or ""

            # Extract token usage
            token_usage = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }

            metadata = {
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
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
            error_msg = f"OpenAI API error: {str(e)}"

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
        """Check if model_id is a valid GPT model"""
        return model_id in self.VALID_MODELS
