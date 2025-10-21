from typing import Dict, Any
from openai import AsyncOpenAI
from ai3core.env import require_env


class OpenAIProvider:
    """OpenAI GPT provider."""

    def __init__(self, model: str = "gpt-4", max_tokens: int = 4096, temperature: float = 0.7):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = require_env("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content or ""

            # Calculate cost based on model
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            # GPT-4 pricing (approximate)
            if "gpt-4" in self.model.lower():
                cost = (input_tokens * 0.03 / 1000) + (output_tokens * 0.06 / 1000)
            else:  # GPT-3.5
                cost = (input_tokens * 0.001 / 1000) + (output_tokens * 0.002 / 1000)

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
            raise RuntimeError(f"OpenAI API error: {e}")
