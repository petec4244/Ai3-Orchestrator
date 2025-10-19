"""
API Client Wrappers - Interfaces for different AI model APIs
"""

import requests
import time
import logging
from typing import Optional
from anthropic import Anthropic
import openai

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for API clients with retry logic"""

    def __init__(self, api_key: str, max_retries: int = 3):
        self.api_key = api_key
        self.max_retries = max_retries

    def _retry_request(self, func, *args, **kwargs):
        """Retry logic for API requests"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise


class GrokClient(BaseAPIClient):
    """Client for xAI Grok API"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def complete(self, prompt: str, max_tokens: int = 2000) -> str:
        """Get completion from Grok"""
        def _request():
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']

        return self._retry_request(_request)

    def refine_prompt(self, original_prompt: str) -> str:
        """Use Grok to refine/enhance a prompt for coding tasks"""
        refinement_request = f"""As an expert prompt engineer, refine the following prompt to be more specific, detailed, and effective for a coding task. Focus on:
- Clarifying requirements and constraints
- Specifying desired code structure and best practices
- Adding relevant technical details
- Making success criteria explicit

Original prompt:
{original_prompt}

Provide ONLY the refined prompt, without any explanation or meta-commentary."""

        return self.complete(refinement_request, max_tokens=1000)


class ClaudeClient(BaseAPIClient):
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)

    def complete(self, prompt: str, max_tokens: int = 4000) -> str:
        """Get completion from Claude"""
        def _request():
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text

        return self._retry_request(_request)


class ChatGPTClient(BaseAPIClient):
    """Client for OpenAI ChatGPT API"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = openai.OpenAI(api_key=api_key)

    def complete(self, prompt: str, max_tokens: int = 2000) -> str:
        """Get completion from ChatGPT"""
        def _request():
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content

        return self._retry_request(_request)
