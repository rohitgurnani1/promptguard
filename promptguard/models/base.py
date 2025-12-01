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

class BaseLLMClient(ABC):
    """Base class for LLM clients that support chat interface."""
    
    @abstractmethod
    def chat(self, messages: List[Message]) -> str:
        """
        Chat with the model using a list of messages.
        
        Args:
            messages: List of Message objects with role and content
            
        Returns:
            The generated response text
        """
        ...

class BaseModel(ABC):
    """Abstract base class for all model implementations."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            The generated response text
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary containing model metadata
        """
        pass
