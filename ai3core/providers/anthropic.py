from typing import Dict, Any
import anthropic
from ai3core.env import require_env


class AnthropicProvider:
    """Anthropic Claude provider."""

    def __init__(self, model: str = "claude-3-7-sonnet-latest", max_tokens: int = 4096, temperature: float = 0.7):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = require_env("ANTHROPIC_API_KEY")
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract text content
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text

            # Calculate approximate cost (Claude 3.7 Sonnet pricing)
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)

            return {
                "content": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "cost": cost
                }
            }
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
