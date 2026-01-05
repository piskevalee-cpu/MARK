"""
MARK Memory Manager

Handles storage, retrieval, and search of persistent memories.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from ..database import MemoryDB


class MemoryManager:
    """
    Manages persistent memory storage and retrieval for MARK.
    
    Provides methods to:
    - Parse and save memory commands ("ricorda che...")
    - Search and retrieve relevant memories
    - Format memories for AI context
    """
    
    # Patterns for detecting memory commands (Italian + English)
    MEMORY_PATTERNS = [
        # Italian patterns
        r"ricorda(?:ti)? che (.+)",
        r"memorizza che (.+)",
        r"tieni a mente che (.+)",
        r"salva che (.+)",
        r"ricorda:?\s*(.+)",
        # English patterns
        r"remember that (.+)",
        r"memorize that (.+)",
        r"save that (.+)",
        r"keep in mind that (.+)",
        r"note that (.+)",
    ]
    
    # Patterns for memory query requests
    QUERY_PATTERNS = [
        # Italian patterns
        r"cosa (sai|ricordi) (di|su) me",
        r"come (sono|mi chiamo)",
        r"chi sono",
        r"cosa ti ho detto",
        r"cosa (hai|ricordi) memorizzato",
        r"quali sono le (mie )?informazioni",
        # English patterns  
        r"what do you (know|remember) about me",
        r"who am i",
        r"what('s| is) my name",
        r"what did i tell you",
        r"what have you memorized",
    ]
    
    def __init__(self, db: Optional[MemoryDB] = None):
        """
        Initialize the memory manager.
        
        Args:
            db: Optional MemoryDB instance. Creates new one if not provided.
        """
        self.db = db or MemoryDB()
    
    def is_memory_command(self, message: str) -> bool:
        """
        Check if a message is a memory save command.
        
        Args:
            message: The user's message
            
        Returns:
            True if it's a memory command
        """
        message_lower = message.lower().strip()
        for pattern in self.MEMORY_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        return False
    
    def parse_memory_command(self, message: str) -> Optional[Tuple[str, str]]:
        """
        Parse a memory command and extract key-value pair.
        
        Args:
            message: The user's message containing a memory command
            
        Returns:
            Tuple of (key, value) or None if not a valid command
        """
        message_lower = message.lower().strip()
        
        for pattern in self.MEMORY_PATTERNS:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Extract a key from the value
                # Try to find a subject (e.g., "mi chiamo Marco" -> key="nome")
                key = self._extract_key(value)
                
                # Get the original case value
                original_match = re.search(pattern, message, re.IGNORECASE)
                if original_match:
                    value = original_match.group(1).strip()
                
                return (key, value)
        
        return None
    
    def _extract_key(self, value: str) -> str:
        """
        Extract a meaningful key from a memory value.
        
        Args:
            value: The memory value text
            
        Returns:
            An extracted or generated key
        """
        value_lower = value.lower()
        
        # Common patterns for key extraction
        key_patterns = {
            r"mi chiamo|my name is|sono": "nome",
            r"ho (\d+) anni|i am (\d+) years old": "età",
            r"abito|vivo|live in": "residenza",
            r"lavoro|work as|sono un": "lavoro",
            r"mi piace|like|love|amo": "preferenze",
            r"odio|hate|detesto": "antipatie",
            r"compleanno|birthday|nato": "data_nascita",
            r"email|mail": "email",
            r"telefono|phone|numero": "telefono",
        }
        
        for pattern, key in key_patterns.items():
            if re.search(pattern, value_lower):
                return key
        
        # Default: use first few words
        words = value.split()[:3]
        return "_".join(words).lower().replace(".", "").replace(",", "")
    
    def save_memory(
        self, 
        key: str, 
        value: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save a memory to the database.
        
        Args:
            key: Memory key/category
            value: Memory content
            metadata: Optional additional data
            
        Returns:
            The memory ID
        """
        return self.db.add_memory(key, value, metadata)
    
    def process_memory_command(self, message: str) -> Tuple[bool, str]:
        """
        Process a message that might be a memory command.
        
        Args:
            message: The user's message
            
        Returns:
            Tuple of (success, response_message)
        """
        parsed = self.parse_memory_command(message)
        
        if parsed:
            key, value = parsed
            memory_id = self.save_memory(key, value)
            return (True, f"✅ I will memorize: \"{value}\" (ID: {memory_id})")
        
        return (False, "I didn't understand what to memorize.")
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memories by query.
        
        Args:
            query: Search term
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        return self.db.search_memories(query, limit)
    
    def get_relevant_memories(
        self, 
        user_message: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get memories relevant to the user's message.
        
        This method extracts keywords from the message and searches
        for related memories.
        
        Args:
            user_message: The user's message
            limit: Maximum memories to return
            
        Returns:
            List of relevant memories
        """
        # STRATEGY CHANGE:
        # Instead of strict keyword matching (which fails cross-language),
        # we will provide the most recent memories to the LLM and let it deciding relevance.
        # This is more robust for a personal assistant with acceptable context window usage.
        
        # If it seems like a specific query or we have space, just give everything (up to limit)
        # We increase default limit if not specified
        effective_limit = limit if limit > 10 else 20
        
        return self.db.list_memories(limit=effective_limit)
    
    def _is_memory_query(self, message: str) -> bool:
        """Check if the message is asking about stored memories."""
        message_lower = message.lower()
        for pattern in self.QUERY_PATTERNS:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def format_memories_for_context(
        self, 
        memories: List[Dict[str, Any]]
    ) -> str:
        """
        Format memories for inclusion in AI context.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Formatted string for AI context
        """
        if not memories:
            return ""
        
        lines = []
        for mem in memories:
            timestamp = mem.get("timestamp", "")[:10]  # Just date
            key = mem.get("key", "info")
            value = mem.get("value", "")
            lines.append(f"- [{key}] {value}")
        
        return "\n".join(lines)
    
    def list_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all memories."""
        return self.db.list_memories(limit)
    
    def delete(self, memory_id: int) -> bool:
        """Delete a memory by ID."""
        return self.db.delete_memory(memory_id)
    
    def clear_all(self) -> int:
        """Clear all memories. Returns count of deleted."""
        return self.db.clear_memories()
