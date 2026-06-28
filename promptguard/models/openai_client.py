# OpenAI client for PromptGuard

from typing import Dict, Any, Optional, List
from openai import OpenAI
from .base import BaseModel, BaseLLMClient, Message, ChatResult
from ..config import Config


class OpenAIClient(BaseModel, BaseLLMClient):
    """OpenAI API client wrapper."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[Any] = None,
    ):
        if config is not None:
            self.model = config.model_name
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
        else:
            self.model = model or Config.OPENAI_MODEL
            self.max_tokens = Config.DEFAULT_MAX_TOKENS
            self.temperature = Config.DEFAULT_TEMPERATURE

        self.api_key = api_key or Config.OPENAI_API_KEY

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self._client = OpenAI(api_key=self.api_key)

    def _create_completion(self, messages_dict: List[Dict[str, str]]):
        base_kwargs = {
            "model": self.model,
            "messages": messages_dict,
        }

        try:
            return self._client.chat.completions.create(
                **base_kwargs,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "max_tokens" in error_msg and "max_completion_tokens" in error_msg:
                try:
                    return self._client.chat.completions.create(
                        **base_kwargs,
                        temperature=self.temperature,
                        max_completion_tokens=self.max_tokens,
                    )
                except Exception as e2:
                    error_msg2 = str(e2).lower()
                    if "temperature" in error_msg2:
                        return self._client.chat.completions.create(
                            **base_kwargs,
                            max_completion_tokens=self.max_tokens,
                        )
                    raise
            elif "temperature" in error_msg:
                try:
                    return self._client.chat.completions.create(
                        **base_kwargs,
                        max_tokens=self.max_tokens,
                    )
                except Exception as e2:
                    error_msg2 = str(e2).lower()
                    if "max_tokens" in error_msg2 and "max_completion_tokens" in error_msg2:
                        return self._client.chat.completions.create(
                            **base_kwargs,
                            max_completion_tokens=self.max_tokens,
                        )
                    raise
            raise

    def _response_to_result(self, response) -> ChatResult:
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        if usage is None:
            return ChatResult(content=content)

        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0
        total_tokens = getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or 0
        return ChatResult(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    def chat_with_metadata(self, messages: List[Message]) -> ChatResult:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in messages]
        response = self._create_completion(messages_dict)
        return self._response_to_result(response)

    def chat(self, messages: List[Message]) -> str:
        return self.chat_with_metadata(messages).content

    def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model,
            "api_key_set": bool(self.api_key),
        }
