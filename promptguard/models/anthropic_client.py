"""Anthropic API client for PromptGuard."""

from typing import Dict, Any, List, Optional

from .base import BaseModel, BaseLLMClient, Message, ChatResult
from ..config import Config, ModelConfig


class AnthropicClient(BaseModel, BaseLLMClient):
    """Anthropic Messages API client wrapper."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
    ):
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "Anthropic support requires the anthropic package. "
                "Install with: pip install anthropic"
            ) from exc

        if config is not None:
            self.model = config.model_name
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
        else:
            self.model = model or "claude-3-5-haiku-latest"
            self.max_tokens = Config.DEFAULT_MAX_TOKENS
            self.temperature = Config.DEFAULT_TEMPERATURE

        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self._client = anthropic.Anthropic(api_key=self.api_key)

    def _split_messages(self, messages: List[Message]):
        system_parts = []
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_parts.append(msg.content)
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})
        return "\n\n".join(system_parts), chat_messages

    def chat_with_metadata(self, messages: List[Message]) -> ChatResult:
        system, chat_messages = self._split_messages(messages)
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": chat_messages,
            "temperature": self.temperature,
        }
        if system:
            kwargs["system"] = system

        response = self._client.messages.create(**kwargs)
        content = ""
        for block in response.content:
            if getattr(block, "type", None) == "text":
                content += block.text

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "output_tokens", 0) if usage else 0
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
            "provider": "anthropic",
            "model": self.model,
            "api_key_set": bool(self.api_key),
        }
