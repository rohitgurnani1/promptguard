"""
Base attack interface for PromptGuard.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAttack(ABC):
    """Abstract base class for all prompt injection attacks."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize attack.
        
        Args:
            name: Name of the attack
            description: Description of the attack
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def generate(self, target_prompt: str, **kwargs) -> str:
        """
        Generate an attack prompt.
        
        Args:
            target_prompt: The original prompt to attack
            **kwargs: Additional attack parameters
            
        Returns:
            The attack prompt
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the attack.
        
        Returns:
            Dictionary containing attack metadata
        """
        return {
            "name": self.name,
            "description": self.description,
        }

