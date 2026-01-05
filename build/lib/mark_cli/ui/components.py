"""
MARK UI Components

Reusable Rich components for the terminal interface.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


# =============================================================================
# Color Scheme
# =============================================================================

COLORS = {
    "primary": "#e11d48",      # Rose 600 (Red)
    "secondary": "#be123c",    # Rose 700 (Darker Red)
    "success": "#22c55e",      # Green
    "warning": "#f59e0b",      # Amber
    "error": "#9f1239",        # Rose 800 (Deep Red for errors)
    "info": "#fb7185",         # Rose 400 (Lighter Red)
    "muted": "#6b7280",        # Gray
    "user": "#fda4af",         # Rose 300 (Very Light Red)
    "ai": "#e11d48",           # Rose 600 (Primary Red)
    "border": "#be123c",       # Rose 700
    "kleos": "#fde047",        # Yellow 300
}


# =============================================================================
# Header Panel
# =============================================================================

class HeaderPanel:
    """Header component showing app name, model, and status."""
    
    def __init__(
        self, 
        model: str = "gemini-1.5-flash",
        provider: str = "gemini",
        connected: bool = True
    ):
        self.model = model
        self.provider = provider
        self.connected = connected
    
    def render(self) -> Panel:
        """Render the header panel."""
        # Build status indicator
        status_icon = "●" if self.connected else "○"
        status_color = COLORS["success"] if self.connected else COLORS["error"]
        status_text = "Connected" if self.connected else "Disconnected"
        
        # Create header text
        header = Text()
        header.append("MARK", style=f"bold {COLORS['primary']}")
        header.append(" | ", style=COLORS["muted"])
        header.append(f"{self.provider.upper()}", style=f"bold {COLORS['secondary']}")
        header.append(f" [{self.model}]", style=COLORS["muted"])
        header.append(" | ", style=COLORS["muted"])
        header.append(f"{status_icon} ", style=status_color)
        header.append(status_text, style=status_color)
        
        return Panel(
            header,
            border_style=COLORS["border"],
            padding=(0, 1),
        )
    
    def update(self, model: str = None, provider: str = None, connected: bool = None):
        """Update header values."""
        if model is not None:
            self.model = model
        if provider is not None:
            self.provider = provider
        if connected is not None:
            self.connected = connected


# =============================================================================
# Usage Panel
# =============================================================================

class UsagePanel:
    """Panel showing API usage statistics."""
    
    def __init__(
        self,
        tokens_used: int = 0,
        tokens_limit: int = 1000000,
        requests_count: int = 0,
        rate_limit_ok: bool = True
    ):
        self.tokens_used = tokens_used
        self.tokens_limit = tokens_limit
        self.requests_count = requests_count
        self.rate_limit_ok = rate_limit_ok
    
    def render(self) -> Panel:
        """Render the usage panel."""
        content = Text()
        
        # Title
        content.append("USAGE\n", style=f"bold {COLORS['info']}")
        
        # Tokens
        tokens_pct = (self.tokens_used / self.tokens_limit * 100) if self.tokens_limit > 0 else 0
        tokens_color = COLORS["success"] if tokens_pct < 80 else (COLORS["warning"] if tokens_pct < 95 else COLORS["error"])
        
        content.append("├─ ", style=COLORS["muted"])
        content.append("Token: ", style="bold")
        content.append(f"{self.tokens_used:,}", style=tokens_color)
        content.append(f" / {self.tokens_limit:,}\n", style=COLORS["muted"])
        
        # Requests
        content.append("├─ ", style=COLORS["muted"])
        content.append("Requests: ", style="bold")
        content.append(f"{self.requests_count}\n", style=COLORS["info"])
        
        # Rate limit
        rate_icon = "✓" if self.rate_limit_ok else "⚠"
        rate_color = COLORS["success"] if self.rate_limit_ok else COLORS["warning"]
        rate_text = "OK" if self.rate_limit_ok else "Limited"
        
        content.append("└─ ", style=COLORS["muted"])
        content.append("Rate Limit: ", style="bold")
        content.append(f"{rate_icon} ", style=rate_color)
        content.append(rate_text, style=rate_color)
        
        return Panel(
            content,
            border_style=COLORS["border"],
            padding=(0, 1),
            width=30,
        )
    
    def update(
        self,
        tokens_used: int = None,
        requests_count: int = None,
        rate_limit_ok: bool = None
    ):
        """Update usage values."""
        if tokens_used is not None:
            self.tokens_used = tokens_used
        if requests_count is not None:
            self.requests_count = requests_count
        if rate_limit_ok is not None:
            self.rate_limit_ok = rate_limit_ok


# =============================================================================
# Message Panel
# =============================================================================

class MessagePanel:
    """Panel for displaying chat messages."""
    
    @staticmethod
    def user_message(content: str, user_name: str = "User", timestamp: Optional[str] = None) -> Panel:
        """Render a user message."""
        from rich import box
        text = Text()
        text.append(f"{user_name}", style=f"bold {COLORS['user']}")
        
        if timestamp:
            text.append(f" | {timestamp}", style=COLORS["muted"])
        
        return Panel(
            content,
            title=text,
            title_align="left",
            border_style=COLORS["user"],
            padding=(0, 1),
            box=box.ROUNDED
        )
    
    @staticmethod
    def ai_message(content: Any, model: str = "", timestamp: Optional[str] = None, style: str = "ai", is_streaming: bool = False) -> Panel:
        """Render an AI response message with markdown support or direct renderable."""
        from rich import box
        from rich.markdown import Markdown
        title = Text()
        
        if style == "kleos":
            display_name = "Kleòs"
        else:
            display_name = "MARK" if style == "ai" else style.upper()
            
        color = COLORS.get(style, COLORS["ai"])
        title.append(display_name, style=f"bold {color}")
        
        if model:
            title.append(f" [{model}]", style=COLORS["muted"])
        
        if timestamp:
            title.append(f" | {timestamp}", style=COLORS["muted"])
        
        # Always treat as Markdown for consistency unless it's already a renderable
        renderable = Markdown(content) if isinstance(content, str) else content
        
        return Panel(
            renderable,
            title=title,
            title_align="left",
            border_style=COLORS[style],
            padding=(0, 1),
            box=box.ROUNDED
        )
    
    @staticmethod
    def system_message(content: str, style: str = "info") -> Panel:
        """Render a system message."""
        colors = {
            "info": COLORS["info"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"],
            "kleos": COLORS["kleos"],
        }
        
        color = colors.get(style, colors["info"])
        title = "KLEÒS SYSTEM" if style == "kleos" else "SYSTEM"
        
        return Panel(
            content,
            title=title,
            title_align="left",
            border_style=color,
            padding=(0, 1),
        )



# =============================================================================
# Error Panel
# =============================================================================

class ErrorPanel:
    """Panel for displaying errors."""
    
    @staticmethod
    def render(
        message: str, 
        title: str = "Error",
        suggestion: Optional[str] = None
    ) -> Panel:
        """Render an error panel."""
        content = Text()
        content.append(message, style="bold")
        
        if suggestion:
            content.append("\n\n💡 ", style="bold")
            content.append(suggestion, style=COLORS["muted"])
        
        return Panel(
            content,
            title=f"❌ {title}",
            title_align="left",
            border_style=COLORS["error"],
            padding=(0, 1),
        )


# =============================================================================
# Help Table
# =============================================================================

class HelpTable:
    """Table showing available commands."""
    
    COMMANDS = [
        ("/help", "Show this help message"),
        ("/clear", "Clear screen"),
        ("/model", "Change provider & model"),
        ("/kleos", "Deep reasoning mode (Analyst + Thinker)"),
        ("/stats", "Show detailed statistics"),
        ("/memory", "Memory mgmt (list, search, delete)"),
        ("/config", "Modify configuration"),
        ("/changeusr", "Change username"),
        ("/reset", "Reset chat session"),
        ("/quit, /exit", "Exit MARK"),
        ("Ctrl+C", "Stop AI response"),
    ]
    
    @classmethod
    def render(cls) -> Panel:
        """Render the help table."""
        table = Table(
            show_header=True,
            header_style=f"bold {COLORS['primary']}",
            border_style=COLORS["border"],
            padding=(0, 1),
        )
        
        table.add_column("Command", style=f"bold {COLORS['info']}")
        table.add_column("Description")
        
        for cmd, desc in cls.COMMANDS:
            table.add_row(cmd, desc)
        
        # Add memory commands section
        table.add_row("", "")
        table.add_row(
            "remember that...", 
            "Save info to memory",
            style=COLORS["secondary"]
        )
        
        return Panel(
            table,
            title="AVAILABLE COMMANDS",
            title_align="left",
            border_style=COLORS["primary"],
            padding=(0, 1),
        )


# =============================================================================
# Loading Spinner
# =============================================================================

class LoadingSpinner:
    """Animated loading spinner."""
    
    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.progress = Progress(
            SpinnerColumn("dots"),
            TextColumn("[bold purple]{task.description}"),
            transient=True,
        )
        self._task_id = None
    
    def __enter__(self):
        """Context manager enter."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def start(self):
        """Start the spinner."""
        self.progress.start()
        self._task_id = self.progress.add_task(self.message)
    
    def stop(self):
        """Stop the spinner."""
        if self._task_id is not None:
            self.progress.remove_task(self._task_id)
        self.progress.stop()
    
    def update_message(self, message: str):
        """Update the spinner message."""
        if self._task_id is not None:
            self.progress.update(self._task_id, description=message)


# =============================================================================
# Footer Bar
# =============================================================================

class FooterBar:
    """Footer showing keyboard shortcuts."""
    
    @staticmethod  
    def render() -> Text:
        """Render the footer bar."""
        footer = Text()
        footer.append("  /help", style=f"bold {COLORS['info']}")
        footer.append(" help", style=COLORS["muted"])
        footer.append("  │  ", style=COLORS["border"])
        footer.append("Ctrl+C/S", style=f"bold {COLORS['warning']}")
        footer.append(" interrupt", style=COLORS["muted"])
        footer.append("  │  ", style=COLORS["border"])
        footer.append("/quit", style=f"bold {COLORS['error']}")
        footer.append(" exit", style=COLORS["muted"])
        
        return footer


# =============================================================================
# Memory List
# =============================================================================

class MemoryList:
    """Component for displaying memories."""
    
    @staticmethod
    def render(memories: List[Dict[str, Any]]) -> Panel:
        """Render a list of memories."""
        if not memories:
            return Panel(
                "No memories saved.",
                title="🧠 Memories",
                title_align="left",
                border_style=COLORS["muted"],
            )
        
        table = Table(
            show_header=True,
            header_style=f"bold {COLORS['secondary']}",
            border_style=COLORS["border"],
        )
        
        table.add_column("ID", style=COLORS["muted"], width=4)
        table.add_column("Key", style=f"bold {COLORS['info']}", width=15)
        table.add_column("Value", ratio=1)
        table.add_column("Date", style=COLORS["muted"], width=10)
        
        for mem in memories:
            table.add_row(
                str(mem.get("id", "")),
                mem.get("key", ""),
                mem.get("value", "")[:50] + ("..." if len(mem.get("value", "")) > 50 else ""),
                str(mem.get("timestamp", ""))[:10],
            )
        
        return Panel(
            table,
            title="SAVED MEMORIES",
            title_align="left",
            border_style=COLORS["secondary"],
        )


# =============================================================================
# Stats Panel
# =============================================================================

class StatsPanel:
    """Detailed statistics panel."""
    
    @staticmethod
    def render(
        session_stats: Dict[str, Any],
        db_stats: Dict[str, Any],
        provider: str,
        model: str
    ) -> Panel:
        """Render detailed statistics."""
        table = Table(
            show_header=False,
            border_style=COLORS["border"],
            padding=(0, 1),
        )
        
        table.add_column("Stat", style=f"bold {COLORS['muted']}")
        table.add_column("Value", style=COLORS["info"])
        
        # Session stats
        table.add_row("CURRENT SESSION", "", style=f"bold {COLORS['primary']}")
        table.add_row("  Token Input", f"{session_stats.get('tokens_input', 0):,}")
        table.add_row("  Token Output", f"{session_stats.get('tokens_output', 0):,}")
        table.add_row("  Total Tokens", f"{session_stats.get('tokens_total', 0):,}")
        table.add_row("  Requests", str(session_stats.get('requests_count', 0)))
        table.add_row("", "")
        
        # DB stats (last 30 days)
        table.add_row("LAST 30 DAYS", "", style=f"bold {COLORS['secondary']}")
        table.add_row("  Total Requests", str(db_stats.get('request_count', 0)))
        table.add_row("  Total Tokens", f"{db_stats.get('total_tokens', 0):,}")
        table.add_row("", "")
        
        # Provider info
        table.add_row("PROVIDER", "", style=f"bold {COLORS['info']}")
        table.add_row("  Name", provider.upper())
        table.add_row("  Model", model)
        
        return Panel(
            table,
            title="DETAILED STATISTICS",
            title_align="left",
            border_style=COLORS["primary"],
        )
