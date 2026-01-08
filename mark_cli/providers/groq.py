"""
MARK Groq Provider

Implementation of the AI provider for Groq's models.
Supports GPT-OSS 120B, Llama 70B Versatile, and Kimi K2.
"""

import asyncio
from typing import Any, Dict, List, Optional

from groq import Groq

from .base import AIProvider, AIResponse, Message, UsageStats


class GroqProvider(AIProvider):
    """
    Groq AI Provider implementation.
    
    Supports:
    - openai/gpt-oss-120b (GPT-OSS 120B)
    - llama-3.3-70b-versatile (Llama 70B Versatile)
    - moonshotai/Kimi-K2-Instruct (Kimi K2)
    """
    
    MODELS = [
        "groq/compound",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "moonshotai/Kimi-K2-Instruct",
    ]
    
    # Display names for UI
    MODEL_DISPLAY_NAMES = {
        "openai/gpt-oss-120b": "GPT-OSS 120B",
        "llama-3.3-70b-versatile": "Llama 70B Versatile",
        "moonshotai/Kimi-K2-Instruct": "Kimi K2",
        "groq/compound": "Groq Compound",
    }
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__(api_key, model)
        self._client = Groq(api_key=api_key)
    
    @property
    def provider_name(self) -> str:
        return "groq"
    
    @property
    def available_models(self) -> List[str]:
        return self.MODELS
    
    def set_model(self, model: str) -> bool:
        """Change the model being used."""
        if model in self.available_models:
            self.model = model
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
        Send a message to Groq and get a response.
        """
        try:
            # Build messages list
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add memories
            if memories:
                memory_content = (
                    f"--- MEMORY CONTEXT ---\n"
                    f"<MEMORIES>\n{memories}\n</MEMORIES>\n"
                    f"----------------------"
                )
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] += f"\n\n{memory_content}"
                else:
                    messages.insert(0, {"role": "system", "content": memory_content})
            
            # Add conversation history
            if context:
                for msg in context:
                    role = "user" if msg.role == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call in thread pool for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=8192,
                )
            )
            
            # Extract content
            content = response.choices[0].message.content if response.choices else ""
            
            # Extract usage stats
            usage = UsageStats()
            if hasattr(response, "usage") and response.usage:
                usage.tokens_input = getattr(response.usage, "prompt_tokens", 0)
                usage.tokens_output = getattr(response.usage, "completion_tokens", 0)
                usage.tokens_total = getattr(response.usage, "total_tokens", 0)
            
            # Update session usage
            self.update_session_usage(usage)
            
            # Get finish reason
            finish_reason = None
            if response.choices:
                finish_reason = response.choices[0].finish_reason
            
            return AIResponse(
                content=content,
                model=self.model,
                usage=usage,
                finish_reason=finish_reason,
                raw_response=response,
            )
            
        except Exception as e:
            error_msg = str(e)
            
            if "401" in error_msg or "invalid_api_key" in error_msg.lower():
                raise ValueError("Invalid API key. Please check your Groq API key.")
            elif "429" in error_msg or "rate_limit" in error_msg.lower():
                raise RuntimeError("Rate limit exceeded. Please wait and try again.")
            else:
                raise RuntimeError(f"Groq Error: {error_msg}")

    async def stream_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ):
        """Streaming version of send_message."""
        try:
            # Build messages list
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if memories:
                memory_content = (
                    f"--- MEMORY CONTEXT ---\n"
                    f"<MEMORIES>\n{memories}\n</MEMORIES>\n"
                    f"----------------------"
                )
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] += f"\n\n{memory_content}"
                else:
                    messages.insert(0, {"role": "system", "content": memory_content})
            
            if context:
                for msg in context:
                    role = "user" if msg.role == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})
            
            messages.append({"role": "user", "content": message})
            
            # Create streaming response
            loop = asyncio.get_event_loop()
            stream = await loop.run_in_executor(
                None,
                lambda: self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=8192,
                    stream=True,
                )
            )
            
            # Yield chunks
            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content is not None:
                         yield delta.content
                    
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg.lower():
                raise ValueError("Invalid API key.")
            elif "429" in error_msg or "rate_limit" in error_msg.lower():
                raise RuntimeError("Rate limit exceeded.")
            else:
                raise RuntimeError(f"Groq Streaming Error: {error_msg}")

    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.
        
        Returns:
            True if the key is valid, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.models.list()
            )
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "name": self.model,
            "display_name": self.MODEL_DISPLAY_NAMES.get(self.model, self.model),
            "provider": "groq",
        }
    
    def reset_chat(self):
        """Reset any chat state. Groq is stateless so this is a no-op."""
        pass
