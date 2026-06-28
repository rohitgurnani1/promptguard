# No defense - baseline for testing

from typing import List
from .base import BaseDefense, DefenseContext, messages_from_context
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
        return messages_from_context(ctx, ctx.system_prompt)

