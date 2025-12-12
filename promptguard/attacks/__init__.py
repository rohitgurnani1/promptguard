"""Attacks module for PromptGuard."""

from .base import BaseAttack
from .library import get_default_attacks

__all__ = ["BaseAttack", "get_default_attacks"]

