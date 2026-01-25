"""
MARK Ollama Provider

Implementation of AI provider for local models via Ollama.
Ollama exposes an OpenAI-compatible API at localhost:11434.
"""

import json
from typing import Any, Dict, List, Optional

import httpx

from .base import AIProvider, AIResponse, Message, UsageStats


class OllamaProvider(AIProvider):
    """
    Ollama Local Model Provider.
    
    Connects to a local Ollama server for inference.
    Supports streaming responses.
    """
    
    DEFAULT_ENDPOINT = "http://localhost:11434"
    
    def __init__(self, api_key: str = "", model: str = "llama3"):
        """
        Initialize the Ollama provider.
        
        Args:
            api_key: Ignored (not needed for local Ollama)
            model: Model name as known to Ollama (e.g., "llama3", "qwen2:7b")
        """
        super().__init__(api_key="local", model=model)
        self._endpoint = self.DEFAULT_ENDPOINT
        self._client = httpx.AsyncClient(timeout=120.0)
    
    @property
    def provider_name(self) -> str:
        return "LOCAL"
    
    @property
    def available_models(self) -> List[str]:
        # Dynamic - fetched from Ollama
        return []
    
    def set_model(self, model: str) -> bool:
        """Change the model."""
        self.model = model
        return True
    
    async def list_models(self) -> List[str]:
        """Fetch available models from Ollama."""
        try:
            response = await self._client.get(f"{self._endpoint}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def _build_messages(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Build messages list for Ollama API."""
        messages = []
        
        # System prompt
        if system_prompt:
            sys_content = system_prompt
            if memories:
                sys_content += (
                    f"\n\n--- MEMORY CONTEXT ---\n"
                    f"<MEMORIES>\n{memories}\n</MEMORIES>\n"
                    f"----------------------"
                )
            messages.append({"role": "system", "content": sys_content})
        elif memories:
            messages.append({
                "role": "system",
                "content": (
                    f"--- MEMORY CONTEXT ---\n"
                    f"<MEMORIES>\n{memories}\n</MEMORIES>\n"
                    f"----------------------"
                )
            })
        
        # Conversation history
        if context:
            for msg in context:
                role = "user" if msg.role == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})
        
        # Current message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    async def send_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ) -> AIResponse:
        """Send a message and get a response (non-streaming)."""
        messages = self._build_messages(message, context, system_prompt, memories)
        
        try:
            response = await self._client.post(
                f"{self._endpoint}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.text}")
            
            data = response.json()
            content = data.get("message", {}).get("content", "")
            
            # Extract usage if available
            usage = UsageStats()
            if "eval_count" in data:
                usage.tokens_output = data.get("eval_count", 0)
                usage.tokens_input = data.get("prompt_eval_count", 0)
                usage.tokens_total = usage.tokens_input + usage.tokens_output
            
            self.update_session_usage(usage)
            
            return AIResponse(
                content=content,
                model=self.model,
                usage=usage,
                finish_reason="stop",
            )
            
        except httpx.ConnectError:
            raise RuntimeError(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running (ollama serve)."
            )
        except Exception as e:
            raise RuntimeError(f"Ollama Error: {e}")
    
    async def stream_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ):
        """Stream a message response."""
        messages = self._build_messages(message, context, system_prompt, memories)
        
        try:
            async with self._client.stream(
                "POST",
                f"{self._endpoint}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise RuntimeError(f"Ollama error: {error_text.decode()}")
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except httpx.ConnectError:
            raise RuntimeError(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running (ollama serve)."
            )
        except Exception as e:
            if "ConnectError" not in str(type(e)):
                raise RuntimeError(f"Ollama Streaming Error: {e}")
            raise
    
    async def validate_api_key(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = await self._client.get(f"{self._endpoint}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "name": self.model,
            "provider": "LOCAL (Ollama)",
            "endpoint": self._endpoint,
        }
    
    def reset_chat(self):
        """Reset chat state (no-op for Ollama, stateless)."""
        pass
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
