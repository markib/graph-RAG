from __future__ import annotations

import os
from typing import Any

from groq import AsyncGroq


class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise RuntimeError(
                'GROQ_API_KEY is not set. Add GROQ_API_KEY to .env to enable LLM queries.'
            )

        self.client = AsyncGroq(api_key=self.api_key)
        self.model = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')

    async def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024,
            temperature=0.2,
        )

        if hasattr(response, "model_dump"):
            return response.model_dump()
        if hasattr(response, "dict"):
            return response.dict()
        return dict(response)
