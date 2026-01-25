"""
MARK Local GGUF Provider

Implementation of AI provider for local GGUF models using llama-cpp-python.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import AIProvider, AIResponse, Message, UsageStats


class LocalGGUFProvider(AIProvider):
    """
    Local GGUF Model Provider using llama-cpp-python.
    
    Loads .gguf files directly and runs inference locally.
    """
    
    def __init__(self, api_key: str = "", model: str = ""):
        """
        Initialize the local provider.
        
        Args:
            api_key: Ignored (not needed for local models)
            model: Path to the .gguf file (absolute or relative to models dir)
        """
        super().__init__(api_key="local", model=model)
        self._llm = None
        self._model_path = model
        
        # Lazy load the model on first use
    
    def _ensure_loaded(self):
        """Load the model if not already loaded."""
        if self._llm is None:
            try:
                from llama_cpp import Llama
            except ImportError:
                raise ImportError(
                    "llama-cpp-python is not installed. "
                    "Install it with: pip install llama-cpp-python"
                )
            
            if not Path(self._model_path).exists():
                raise FileNotFoundError(f"Model file not found: {self._model_path}")
            
            self._llm = Llama(
                model_path=str(self._model_path),
                n_ctx=8192,
                n_threads=None,  # Auto-detect
                verbose=False,
            )
    
    @property
    def provider_name(self) -> str:
        return "LOCAL"
    
    @property
    def available_models(self) -> List[str]:
        # This is dynamic based on files in models/ dir
        # Return empty list; actual discovery happens in main.py
        return []
    
    def set_model(self, model: str) -> bool:
        """Change the model (requires reloading)."""
        if Path(model).exists():
            self._model_path = model
            self._llm = None  # Force reload
            self.model = model
            return True
        return False
    
    def _build_messages(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Build OpenAI-compatible messages list."""
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
        """Send a message and get a response."""
        self._ensure_loaded()
        
        messages = self._build_messages(message, context, system_prompt, memories)
        
        try:
            response = self._llm.create_chat_completion(
                messages=messages,
                max_tokens=2048,
                temperature=0.7,
                stream=False,
            )
            
            content = response["choices"][0]["message"]["content"]
            
            # Extract usage
            usage = UsageStats()
            if "usage" in response:
                usage.tokens_input = response["usage"].get("prompt_tokens", 0)
                usage.tokens_output = response["usage"].get("completion_tokens", 0)
                usage.tokens_total = response["usage"].get("total_tokens", 0)
            
            self.update_session_usage(usage)
            
            return AIResponse(
                content=content,
                model=Path(self._model_path).name,
                usage=usage,
                finish_reason=response["choices"][0].get("finish_reason"),
            )
            
        except Exception as e:
            raise RuntimeError(f"Local Model Error: {e}")
    
    async def stream_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        memories: Optional[str] = None,
    ):
        """Stream a message response."""
        self._ensure_loaded()
        
        messages = self._build_messages(message, context, system_prompt, memories)
        
        try:
            stream = self._llm.create_chat_completion(
                messages=messages,
                max_tokens=2048,
                temperature=0.7,
                stream=True,
            )
            
            for chunk in stream:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta and delta["content"]:
                    yield delta["content"]
                    
        except Exception as e:
            raise RuntimeError(f"Local Model Streaming Error: {e}")
    
    async def validate_api_key(self) -> bool:
        """Local models don't need API key validation."""
        try:
            self._ensure_loaded()
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "name": Path(self._model_path).name,
            "path": str(self._model_path),
            "provider": "LOCAL",
        }
    
    def reset_chat(self):
        """Reset chat state (no-op for local, stateless)."""
        pass
    
    def unload(self):
        """Unload the model to free memory."""
        if self._llm is not None:
            del self._llm
            self._llm = None
