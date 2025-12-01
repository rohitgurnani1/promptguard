"""
Base defense interface for PromptGuard.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
from ..models.base import Message

@dataclass
class DefenseContext:
    """Context for defense application."""
    system_prompt: str
    user_prompt: str

class BaseDefense(ABC):
    """Abstract base class for all prompt injection defenses."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize defense.
        
        Args:
            name: Name of the defense
            description: Description of the defense
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def apply(self, ctx: DefenseContext) -> List[Message]:
        """
        Apply defense and return message list.
        
        Args:
            ctx: Defense context with system and user prompts
            
        Returns:
            List of Message objects
        """
        ...
    
    def defend(self, prompt: str, **kwargs) -> str:
        """
        Legacy defend method for compatibility.
        
        Args:
            prompt: The input prompt to defend
            **kwargs: Additional defense parameters
            
        Returns:
            The defended/modified prompt
        """
        # Default implementation - subclasses should override if needed
        return prompt
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the defense.
        
        Returns:
            Dictionary containing defense metadata
        """
        return {
            "name": self.name,
            "description": self.description,
        }
