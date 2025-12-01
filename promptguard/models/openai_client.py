"""
OpenAI API client implementation for PromptGuard.
"""

from typing import Dict, Any, Optional, List
from openai import OpenAI
from .base import BaseModel, BaseLLMClient, Message
from ..config import Config


class OpenAIClient(BaseModel, BaseLLMClient):
    """OpenAI API client wrapper."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, config: Optional[Any] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to Config.OPENAI_API_KEY)
            model: Model name (defaults to Config.OPENAI_MODEL)
            config: Optional ModelConfig object (if provided, overrides model parameter)
        """
        # Support both direct parameters and config object
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
    
    def chat(self, messages: List[Message]) -> str:
        """
        Chat with the model using a list of messages.
        
        Args:
            messages: List of Message objects with role and content
            
        Returns:
            The generated response text
        """
        # Convert Message objects to dict format
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # Some newer models (like gpt-5-mini) have different parameter requirements
        base_kwargs = {
            "model": self.model,
            "messages": messages_dict,
        }
        
        # Try with temperature and max_tokens first (for older models)
        try:
            response = self._client.chat.completions.create(
                **base_kwargs,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            error_msg = str(e).lower()
            # If max_tokens is not supported, try max_completion_tokens
            if "max_tokens" in error_msg and "max_completion_tokens" in error_msg:
                try:
                    # Try with temperature and max_completion_tokens
                    response = self._client.chat.completions.create(
                        **base_kwargs,
                        temperature=self.temperature,
                        max_completion_tokens=self.max_tokens,
                    )
                except Exception as e2:
                    error_msg2 = str(e2).lower()
                    # If temperature is also not supported, use defaults
                    if "temperature" in error_msg2:
                        response = self._client.chat.completions.create(
                            **base_kwargs,
                            max_completion_tokens=self.max_tokens,
                        )
                    else:
                        raise
            elif "temperature" in error_msg:
                # If only temperature is not supported, try without it
                try:
                    response = self._client.chat.completions.create(
                        **base_kwargs,
                        max_tokens=self.max_tokens,
                    )
                except Exception as e2:
                    error_msg2 = str(e2).lower()
                    if "max_tokens" in error_msg2 and "max_completion_tokens" in error_msg2:
                        response = self._client.chat.completions.create(
                            **base_kwargs,
                            max_completion_tokens=self.max_tokens,
                        )
                    else:
                        raise
            else:
                # Re-raise if it's a different error
                raise
        
        return response.choices[0].message.content or ""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using OpenAI API.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            The generated response text
        """
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
        """
        Get information about the OpenAI model.
        
        Returns:
            Dictionary containing model metadata
        """
        return {
            "provider": "openai",
            "model": self.model,
            "api_key_set": bool(self.api_key),
        }
