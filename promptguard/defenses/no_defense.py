# No defense - baseline for testing

from typing import List
from .base import BaseDefense, DefenseContext
from ..models.base import Message


class NoDefense(BaseDefense):
    """No defense - passes through prompts unchanged for baseline testing."""
    
    def __init__(self):
        super().__init__(
            name="no_defense",
            description="No defense applied - baseline for attack testing"
        )
    
    def apply(self, ctx: DefenseContext) -> List[Message]:
        """Apply no defense - just return the messages as-is."""
        return [
            Message(role="system", content=ctx.system_prompt),
            Message(role="user", content=ctx.user_prompt),
        ]

