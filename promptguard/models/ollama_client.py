"""Ollama local API client for PromptGuard."""

import json
import os
import urllib.error
import urllib.request
from typing import Dict, Any, List, Optional

from .base import BaseModel, BaseLLMClient, Message, ChatResult
from ..config import ModelConfig, Config


class OllamaClient(BaseModel, BaseLLMClient):
    """Ollama /api/chat client (no extra dependencies)."""

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        if config is not None:
            self.model = config.model_name
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
        else:
            self.model = model or "llama3.2"
            self.max_tokens = Config.DEFAULT_MAX_TOKENS
            self.temperature = Config.DEFAULT_TEMPERATURE

        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")

    def chat_with_metadata(self, messages: List[Message]) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectionError(
                f"Could not reach Ollama at {self.base_url}. "
                "Is Ollama running? Start with: ollama serve"
            ) from exc

        content = body.get("message", {}).get("content", "")
        prompt_tokens = body.get("prompt_eval_count", 0) or 0
        completion_tokens = body.get("eval_count", 0) or 0
        total_tokens = prompt_tokens + completion_tokens

        return ChatResult(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    def chat(self, messages: List[Message]) -> str:
        return self.chat_with_metadata(messages).content

    def generate(self, prompt: str, **kwargs) -> str:
        return self.chat([Message(role="user", content=prompt)])

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url,
        }
