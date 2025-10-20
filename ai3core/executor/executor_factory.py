"""
Factory for creating executor instances
"""

from typing import Dict, Optional
from .base import BaseExecutor
from .anthropic_adapter import AnthropicAdapter
from .openai_adapter import OpenAIAdapter
from .xai_adapter import XAIAdapter
from ..types import ModelProvider


class ExecutorFactory:
    """
    Factory for creating and managing executor instances

    Handles initialization and caching of adapters for different providers
    """

    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize the factory

        Args:
            api_keys: Dict mapping provider names to API keys
                     e.g., {"anthropic": "sk-...", "openai": "sk-...", "xai": "..."}
        """
        self.api_keys = api_keys
        self._executors: Dict[ModelProvider, BaseExecutor] = {}

    def get_executor(self, provider: ModelProvider) -> BaseExecutor:
        """
        Get or create executor for a provider

        Args:
            provider: ModelProvider enum value

        Returns:
            BaseExecutor instance for the provider

        Raises:
            ValueError: If API key not configured for provider
        """
        # Check cache
        if provider in self._executors:
            return self._executors[provider]

        # Get API key
        provider_key_map = {
            ModelProvider.ANTHROPIC: "anthropic",
            ModelProvider.OPENAI: "openai",
            ModelProvider.XAI: "xai"
        }

        key_name = provider_key_map.get(provider)
        if not key_name or key_name not in self.api_keys:
            raise ValueError(f"API key not configured for provider: {provider.value}")

        api_key = self.api_keys[key_name]

        # Create executor
        if provider == ModelProvider.ANTHROPIC:
            executor = AnthropicAdapter(api_key)
        elif provider == ModelProvider.OPENAI:
            executor = OpenAIAdapter(api_key)
        elif provider == ModelProvider.XAI:
            executor = XAIAdapter(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider.value}")

        # Cache and return
        self._executors[provider] = executor
        return executor

    def get_executor_for_model(self, model_id: str, registry) -> Optional[BaseExecutor]:
        """
        Get executor for a specific model

        Args:
            model_id: Model identifier
            registry: CapabilityRegistry to lookup model info

        Returns:
            BaseExecutor instance or None if model not found
        """
        capability = registry.get_capability(model_id)
        if not capability:
            return None

        return self.get_executor(capability.provider)

    def clear_cache(self):
        """Clear cached executors"""
        self._executors.clear()
