from typing import Dict, Any
import httpx
from ai3core.env import require_env


class XAIProvider:
    """xAI Grok provider."""

    def __init__(self, model: str = "grok-4-fast", max_tokens: int = 4096, temperature: float = 0.7):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = require_env("XAI_API_KEY")
        self.api_base = "https://api.x.ai/v1"

    async def generate(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Generate response using xAI Grok API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Dict with content, usage, and cost information
        """
        try:
            async with httpx.AsyncClient() as client:
                messages = []

                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})

                messages.append({"role": "user", "content": prompt})

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }

                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()

                data = response.json()

                # Extract response and usage
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})

                # Calculate cost based on model
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                cost = self._calculate_cost(input_tokens, output_tokens)

                return {
                    "content": content,
                    "usage": {
                        "total_tokens": usage.get("total_tokens", 0),
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost": cost
                    },
                    "model": data.get("model", self.model),
                    "finish_reason": data["choices"][0].get("finish_reason")
                }
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"xAI API HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"xAI API error: {e}")

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on xAI pricing.

        Pricing (per 1M tokens):
        - Grok 4: $3.00 input / $15.00 output
        - Grok 4 Fast: $0.20 input / $0.50 output (< 128K context)
        - Grok 4 Fast: $0.50 input / $1.00 output (> 128K context)
        """
        # Convert tokens to millions
        input_millions = input_tokens / 1_000_000
        output_millions = output_tokens / 1_000_000

        if "grok-4-fast" in self.model:
            # Using lower tier pricing (< 128K context)
            # For > 128K, this would need to be adjusted based on actual context
            input_cost = input_millions * 0.20
            output_cost = output_millions * 0.50
        elif "grok-4" in self.model:
            input_cost = input_millions * 3.00
            output_cost = output_millions * 15.00
        elif "grok-3" in self.model:
            # Grok 3 pricing (estimate, adjust as needed)
            input_cost = input_millions * 2.00
            output_cost = output_millions * 10.00
        else:
            # Grok 2 pricing (estimate, adjust as needed)
            input_cost = input_millions * 1.00
            output_cost = output_millions * 5.00

        return input_cost + output_cost
