"""
xAI (Grok) adapter
"""

import time
import requests
from typing import Optional, Dict, Any
from .base import BaseExecutor
from ..types import ExecutionArtifact, ModelProvider, Task


class XAIAdapter(BaseExecutor):
    """Adapter for xAI Grok models"""

    VALID_MODELS = [
        "grok-4",
        "grok-4-fast",
        "grok-4-fast-reasoning",
        "grok-4-fast-non-reasoning",
        "grok-3",
        "grok-2-latest",
        "grok-2"
    ]

    API_BASE_URL = "https://api.x.ai/v1/chat/completions"

    def __init__(self, api_key: str):
        """Initialize xAI adapter"""
        super().__init__(api_key, ModelProvider.XAI)

    def execute(self, task: Task, model_id: str, system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                **kwargs) -> ExecutionArtifact:
        """
        Execute task using Grok

        Args:
            task: Task to execute
            model_id: Grok model to use
            system_prompt: Optional system prompt
            max_tokens: Max output tokens (default 4096)
            temperature: Sampling temperature (default 0.7)
            **kwargs: Additional xAI-specific params

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
            payload = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature or self.default_temperature,
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            # Merge additional kwargs
            payload.update(kwargs)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Make API call
            response = requests.post(
                self.API_BASE_URL,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            latency_ms = (time.time() - start_time) * 1000

            data = response.json()

            # Extract response
            response_text = data["choices"][0]["message"]["content"] or ""

            # Extract token usage
            usage = data.get("usage", {})
            token_usage = {
                "input": usage.get("prompt_tokens", 0),
                "output": usage.get("completion_tokens", 0),
                "total": usage.get("total_tokens", 0)
            }

            metadata = {
                "model": data.get("model", model_id),
                "finish_reason": data["choices"][0].get("finish_reason"),
                "request_id": data.get("id")
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

        except requests.exceptions.RequestException as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"xAI API error: {str(e)}"

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
        """Check if model_id is a valid Grok model"""
        return model_id in self.VALID_MODELS
