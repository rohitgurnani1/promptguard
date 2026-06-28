"""
Base attack interface for PromptGuard.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from promptguard.models.base import Message


class BaseAttack(ABC):
    """Abstract base class for all prompt injection attacks."""

    def __init__(self, name: str, description: str = "", category: str = "direct"):
        self.name = name
        self.description = description
        self.category = category

    @property
    def mode(self) -> str:
        """Attack delivery mode: single, multi_turn, or rag."""
        return "single"

    @abstractmethod
    def build_user_prompt(self, benign_task_prompt: str) -> str:
        """Build the attacked user prompt from a benign task."""
        ...

    def build_messages(self, benign_task_prompt: str) -> List[Message]:
        """Build conversation turns for the attack (default: single user message)."""
        return [Message(role="user", content=self.build_user_prompt(benign_task_prompt))]

    def generate(self, target_prompt: str, **kwargs) -> str:
        """Generate an attack prompt (alias for build_user_prompt)."""
        return self.build_user_prompt(target_prompt)

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "mode": self.mode,
        }
