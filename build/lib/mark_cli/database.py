"""
MARK Database Module

SQLite database management for memories, conversations, and usage tracking.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import DATABASE_PATH


# =============================================================================
# Database Schema
# =============================================================================

SCHEMA = """
-- Memories table: stores user-defined memories
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    metadata TEXT,  -- JSON string
    embedding_vector TEXT  -- For future semantic search
);

-- Conversations table: stores chat history
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0
);

-- API usage table: tracks token usage and costs
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    provider TEXT NOT NULL,
    model TEXT,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER DEFAULT 0,
    cost REAL DEFAULT 0.0
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_provider ON api_usage(provider);
"""


# =============================================================================
# Database Initialization
# =============================================================================

def init_database(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Initialize the database with schema. Returns connection."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    
    # Execute schema
    conn.executescript(SCHEMA)
    conn.commit()
    
    return conn


def get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# Memory Operations
# =============================================================================

class MemoryDB:
    """Database operations for the memory system."""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database and tables exist."""
        if not self.db_path.exists():
            init_database(self.db_path)
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get a new connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    # -------------------------------------------------------------------------
    # Memory CRUD
    # -------------------------------------------------------------------------
    
    def add_memory(
        self, 
        key: str, 
        value: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add a new memory. Returns the memory ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                INSERT INTO memories (key, value, metadata)
                VALUES (?, ?, ?)
                """,
                (key, value, json.dumps(metadata) if metadata else None)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,)
            ).fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()
    
    def search_memories(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by key or value using LIKE."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """
                SELECT * FROM memories 
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit)
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()
    
    def list_memories(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all memories, most recent first."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """
                SELECT * FROM memories 
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory by ID. Returns True if deleted."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def clear_memories(self) -> int:
        """Delete all memories. Returns count of deleted rows."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("DELETE FROM memories")
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    # -------------------------------------------------------------------------
    # Conversation Operations
    # -------------------------------------------------------------------------
    
    def add_conversation(
        self,
        provider: str,
        model: str,
        user_message: str,
        ai_response: str,
        tokens_used: int = 0
    ) -> int:
        """Add a conversation entry. Returns the conversation ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                INSERT INTO conversations 
                (provider, model, user_message, ai_response, tokens_used)
                VALUES (?, ?, ?, ?, ?)
                """,
                (provider, model, user_message, ai_response, tokens_used)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_recent_conversations(
        self, 
        limit: int = 20,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent conversations."""
        conn = self._get_conn()
        try:
            if provider:
                rows = conn.execute(
                    """
                    SELECT * FROM conversations 
                    WHERE provider = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (provider, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM conversations 
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,)
                ).fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()
    
    # -------------------------------------------------------------------------
    # Usage Tracking
    # -------------------------------------------------------------------------
    
    def log_usage(
        self,
        provider: str,
        model: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost: float = 0.0
    ) -> int:
        """Log API usage. Returns the log ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                INSERT INTO api_usage 
                (provider, model, tokens_input, tokens_output, tokens_total, cost)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (provider, model, tokens_input, tokens_output, 
                 tokens_input + tokens_output, cost)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_usage_stats(
        self, 
        provider: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated usage statistics."""
        conn = self._get_conn()
        try:
            if provider:
                row = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as request_count,
                        COALESCE(SUM(tokens_input), 0) as total_input,
                        COALESCE(SUM(tokens_output), 0) as total_output,
                        COALESCE(SUM(tokens_total), 0) as total_tokens,
                        COALESCE(SUM(cost), 0.0) as total_cost
                    FROM api_usage 
                    WHERE provider = ?
                    AND timestamp >= datetime('now', ?)
                    """,
                    (provider, f"-{days} days")
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as request_count,
                        COALESCE(SUM(tokens_input), 0) as total_input,
                        COALESCE(SUM(tokens_output), 0) as total_output,
                        COALESCE(SUM(tokens_total), 0) as total_tokens,
                        COALESCE(SUM(cost), 0.0) as total_cost
                    FROM api_usage 
                    WHERE timestamp >= datetime('now', ?)
                    """,
                    (f"-{days} days",)
                ).fetchone()
            
            return {
                "request_count": row["request_count"],
                "total_input": row["total_input"],
                "total_output": row["total_output"],
                "total_tokens": row["total_tokens"],
                "total_cost": row["total_cost"],
            }
        finally:
            conn.close()
    
    def get_today_usage(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get today's usage statistics."""
        conn = self._get_conn()
        try:
            if provider:
                row = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as request_count,
                        COALESCE(SUM(tokens_total), 0) as total_tokens
                    FROM api_usage 
                    WHERE provider = ?
                    AND date(timestamp) = date('now')
                    """,
                    (provider,)
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as request_count,
                        COALESCE(SUM(tokens_total), 0) as total_tokens
                    FROM api_usage 
                    WHERE date(timestamp) = date('now')
                    """
                ).fetchone()
            
            return {
                "request_count": row["request_count"],
                "total_tokens": row["total_tokens"],
            }
        finally:
            conn.close()
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a sqlite3.Row to a dictionary."""
        d = dict(row)
        # Parse JSON metadata if present
        if "metadata" in d and d["metadata"]:
            try:
                d["metadata"] = json.loads(d["metadata"])
            except json.JSONDecodeError:
                pass
        return d
