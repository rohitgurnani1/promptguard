"""
Base model interface for PromptGuard.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Message:
    """Message object for chat-based interactions."""
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class ChatResult:
    """Model response with optional token usage metadata."""
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class BaseLLMClient(ABC):
    """Base class for LLM clients that support chat interface."""

    @abstractmethod
    def chat(self, messages: List[Message]) -> str:
        """Chat with the model using a list of messages."""
        ...

    def chat_with_metadata(self, messages: List[Message]) -> ChatResult:
        """Chat and return token usage when available."""
        content = self.chat(messages)
        return ChatResult(content=content)


class BaseModel(ABC):
    """Abstract base class for all model implementations."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass
