"""
MARK Gemini Provider

Implementation of the AI provider for Google's Gemini models.
"""

import asyncio
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from .base import AIProvider, AIResponse, Message, UsageStats


class GeminiProvider(AIProvider):
    """
    Google Gemini AI Provider implementation using the new google-genai SDK.
    """
    
    MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash",
        "gemma-3-27b",
        "gemma-3-27b-en",
        "gemma-3-27b-it",
        "gemma-3-27b-de",
        "gemma-3-27b-fr",
        "gemma-3-27b-es",
        "gemini-2.0-flash-exp", 
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
    ]
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        super().__init__(api_key, model)
        
        # Initialize the new SDK Client
        self.client = genai.Client(api_key=api_key)
        self._chat = None
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    @property
    def available_models(self) -> List[str]:
        return self.MODELS
    
    def _get_api_model_name(self, model: str) -> str:
        """Map internal model name to API model ID."""
        if model.startswith("gemma-3"):
            # All Gemma 3 variants map to the same API model for now (usually the Instruct one)
            # Adjust if specific IDs for En/It exist, otherwise they share the ID
            return "gemma-3-27b-it" 
        return model

    def set_model(self, model: str) -> bool:
        """Change the model and reinitialize."""
        if model in self.available_models:
            self.model = model
            self._chat = None  # Reset chat session
            return True
        return False
    
    async def send_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ) -> AIResponse:
        """
        Send a message to Gemini and get a response.
        
        Args:
            message: The user's message
            context: Previous conversation history
            system_prompt: Optional system prompt
            memories: Optional memories to include
            
        Returns:
            AIResponse with content and usage stats
        """
        try:
            # Build conversation history for new SDK
            history = []
            if context:
                for msg in context:
                    role = "user" if msg.role == "user" else "model"
                    history.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))
            
            # Check if model supports system instructions (Gemma does not)
            is_gemma = "gemma" in self.model.lower()
            
            config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=8192,
                system_instruction=system_prompt if system_prompt and not is_gemma else None
            )
            
            # Prepare message
            user_message = message
            if is_gemma and system_prompt:
                 user_message = f"{system_prompt}\n\n{user_message}"

            if memories:
                if is_gemma:
                     sys_prompt_part = f"{system_prompt}\n\n" if system_prompt else ""
                     user_message = (
                         f"{sys_prompt_part}"
                         f"--- MEMORY CONTEXT (TRANSLATE IF NEEDED) ---\n"
                         f"<MEMORIES>\n{memories}\n</MEMORIES>\n"
                         f"------------------------------------------\n\n"
                         f"{message}"
                     )
                else:
                    user_message = f"<MEMORIES>\n{memories}\n</MEMORIES>\n\n{message}"
            
            # Initialize or use existing chat
            if self._chat is None or not history:
                self._chat = self.client.chats.create(
                    model=self._get_api_model_name(self.model),
                    config=config,
                    history=history
                )
            
            # Send message
            response = self._chat.send_message(user_message)
            
            # Extract usage stats
            usage = UsageStats()
            if response.usage_metadata:
                metadata = response.usage_metadata
                usage.tokens_input = metadata.prompt_token_count or 0
                usage.tokens_output = metadata.candidates_token_count or 0
                usage.tokens_total = metadata.total_token_count or 0
            
            # Update session usage
            self.update_session_usage(usage)
            
            # Extract response text
            content = ""
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    content = candidate.content.parts[0].text
            
            # Get finish reason
            finish_reason = None
            if response.candidates:
                finish_reason = str(response.candidates[0].finish_reason)
            
            return AIResponse(
                content=content,
                model=self.model,
                usage=usage,
                finish_reason=finish_reason,
            )
            
        except Exception as e:
            # Handle errors gracefully
            error_msg = str(e)
            
            # Check for common errors
            if "API_KEY_INVALID" in error_msg or "401" in error_msg:
                raise ValueError("Invalid API key. Please check your Gemini API key.")
            elif "RATE_LIMIT" in error_msg or "429" in error_msg:
                raise RuntimeError("Rate limit exceeded. Please wait and try again.")
            elif "SAFETY" in error_msg:
                return AIResponse(
                    content="⚠️ The response was blocked for safety reasons.",
                    model=self.model,
                    usage=UsageStats(),
                    finish_reason="SAFETY",
                )
            else:
                raise RuntimeError(f"Gemini Error: {error_msg}")

    async def stream_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ):
        """Streaming version of send_message."""
        try:
            # Build conversation history
            history = []
            if context:
                for msg in context:
                    role = "user" if msg.role == "user" else "model"
                    history.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))
            
            is_gemma = "gemma" in self.model.lower()
            
            config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=8192,
                system_instruction=system_prompt if system_prompt and not is_gemma else None
            )
            
            # Prepare message
            user_message = message
            if is_gemma and system_prompt:
                 user_message = f"{system_prompt}\n\n{user_message}"

            if memories:
                if is_gemma:
                     user_message = (
                         f"{system_prompt}\n\n" if system_prompt else ""
                         f"--- MEMORY CONTEXT (TRANSLATE IF NEEDED) ---\n"
                         f"<MEMORIES>\n{memories}\n</MEMORIES>\n"
                         f"------------------------------------------\n\n"
                         f"{message}"
                     )
                else:
                    user_message = f"<MEMORIES>\n{memories}\n</MEMORIES>\n\n{message}"
            
            # Initialize or use existing chat
            if self._chat is None or not history:
                self._chat = self.client.chats.create(
                    model=self._get_api_model_name(self.model),
                    config=config,
                    history=history
                )
            
            # Get streaming response
            response_stream = self._chat.send_message_stream(user_message)
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                
                # Update usage metadata if available in this chunk (usually final chunk)
                if chunk.usage_metadata:
                    metadata = chunk.usage_metadata
                    usage = UsageStats(
                        tokens_input=metadata.prompt_token_count or 0,
                        tokens_output=metadata.candidates_token_count or 0,
                        tokens_total=metadata.total_token_count or 0
                    )
                    self.update_session_usage(usage)
            
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "401" in error_msg:
                raise ValueError("Invalid API key.")
            elif "RATE_LIMIT" in error_msg or "429" in error_msg:
                raise RuntimeError("Rate limit exceeded.")
            else:
                raise RuntimeError(f"Gemini Streaming Error: {error_msg}")
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.
        
        Returns:
            True if the key is valid, False otherwise
        """
        try:
            # Try to list models - this validates the key in the new SDK
            # Models is a paginated list, we just try to get the first one
            for _ in self.client.models.list(config={'page_size': 1}):
                return True
            return True # If list is empty but no exception, key is likely valid
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            model_info = self.client.models.get(model=self._get_api_model_name(self.model))
            return {
                "name": model_info.name,
                "display_name": model_info.display_name,
                "description": model_info.description,
                "input_token_limit": model_info.input_token_limit,
                "output_token_limit": model_info.output_token_limit,
            }
        except Exception:
            return {"name": self.model, "error": "Could not fetch model info"}
    
    def reset_chat(self):
        """Reset the chat session."""
        self._chat = None
