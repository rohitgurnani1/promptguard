"""
Base attack interface for PromptGuard.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAttack(ABC):
    """Abstract base class for all prompt injection attacks."""

    def __init__(self, name: str, description: str = "", category: str = "direct"):
        self.name = name
        self.description = description
        self.category = category

    @abstractmethod
    def build_user_prompt(self, benign_task_prompt: str) -> str:
        """Build the attacked user prompt from a benign task."""
        ...

    def generate(self, target_prompt: str, **kwargs) -> str:
        """Generate an attack prompt (alias for build_user_prompt)."""
        return self.build_user_prompt(target_prompt)

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
        }
