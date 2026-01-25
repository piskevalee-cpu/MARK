"""
MARK AI Provider Base Class

Abstract base class for all AI provider implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


@dataclass
class UsageStats:
    """Represents API usage statistics."""
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_total: int = 0
    requests_count: int = 0
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[str] = None


@dataclass
class AIResponse:
    """Represents a response from an AI provider."""
    content: str
    model: str
    usage: UsageStats
    finish_reason: Optional[str] = None
    raw_response: Optional[Any] = None


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    All provider implementations (Gemini, Claude, OpenAI, etc.) 
    must inherit from this class and implement its abstract methods.
    """
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize the provider.
        
        Args:
            api_key: The API key for authentication
            model: The model identifier to use
        """
        self.api_key = api_key
        self.model = model
        self._session_usage = UsageStats()
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'gemini', 'claude', 'openai')."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Return list of available models for this provider."""
        pass
    
    @abstractmethod
    async def send_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ) -> AIResponse:
        """
        Send a message to the AI and get a response.
        
        Args:
            message: The user's message
            context: Previous conversation history
            system_prompt: Optional system prompt to set behavior
            memories: Optional memories context to include
            
        Returns:
            AIResponse with content and usage stats
        """
        pass

    @abstractmethod
    async def stream_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ):
        """
        Send a message and return an async generator for streaming response.
        
        Yields:
            Chunks of the response as they arrive.
        """
        yield
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """
        Validate that the API key is valid.
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def get_session_usage(self) -> UsageStats:
        """Get usage statistics for the current session."""
        return self._session_usage
    
    def update_session_usage(self, usage: UsageStats):
        """Update session usage with new request data."""
        self._session_usage.tokens_input += usage.tokens_input
        self._session_usage.tokens_output += usage.tokens_output
        self._session_usage.tokens_total += usage.tokens_total
        self._session_usage.requests_count += 1
        self._session_usage.rate_limit_remaining = usage.rate_limit_remaining
        self._session_usage.rate_limit_reset = usage.rate_limit_reset
    
    def reset_session_usage(self):
        """Reset session usage statistics."""
        self._session_usage = UsageStats()
    
    def set_model(self, model: str) -> bool:
        """
        Change the model being used.
        
        Args:
            model: The new model identifier
            
        Returns:
            True if model is valid and set, False otherwise
        """
        if model in self.available_models:
            self.model = model
            return True
        return False
