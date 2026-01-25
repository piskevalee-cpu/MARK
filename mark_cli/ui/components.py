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
# Color Scheme & Themes
# =============================================================================

THEMES = {
    "red": {
        "primary": "#e11d48",      # Rose 600
        "secondary": "#be123c",    # Rose 700
        "success": "#22c55e",      # Green
        "warning": "#f59e0b",      # Amber
        "error": "#9f1239",        # Rose 800
        "info": "#fb7185",         # Rose 400
        "muted": "#6b7280",        # Gray
        "user": "#fda4af",         # Rose 300
        "ai": "#e11d48",
        "border": "#be123c",
        "kleos": "#fde047",
    },
    "hl3": {
        "primary": "#f89b1c",      # Lambda Orange
        "secondary": "#fa7132",    # Lighter Orange
        "success": "#a2ad91",      # HEV Grayish
        "warning": "#fdec6e",
        "error": "#9c1216",        # Black Mesa Red
        "info": "#ffffff",
        "muted": "#808080",
        "user": "#f89b1c",
        "ai": "#fa7132",
        "border": "#303030",
        "kleos": "#fde047",
    },
    "matrix": {
        "primary": "#00ff41",      # Matrix Green
        "secondary": "#008f11",    # Darker Green
        "success": "#d1ffd1",
        "warning": "#f59e0b",
        "error": "#ff0000",
        "info": "#00ff41",
        "muted": "#003b00",
        "user": "#00ff41",
        "ai": "#008f11",
        "border": "#00ff41",
        "kleos": "#fde047",
    },
    "cyberpunk": {
        "primary": "#fcee0a",      # Cyberpunk Yellow
        "secondary": "#ff003c",    # Cyberpunk Pink
        "success": "#00ebff",      # Cyan
        "warning": "#f3e600",
        "error": "#f61e44",
        "info": "#00ebff",
        "muted": "#02d7f2",
        "user": "#fcee0a",
        "ai": "#ff003c",
        "border": "#fcee0a",
        "kleos": "#fde047",
    },
    "synthwave": {
        "primary": "#ff7edb",      # Pink
        "secondary": "#b893ff",    # Purple
        "success": "#03edf9",      # Cyan
        "warning": "#ff8b39",      # Orange
        "error": "#fe4450",
        "info": "#03edf9",
        "muted": "#241734",
        "user": "#ff7edb",
        "ai": "#b893ff",
        "border": "#ff7edb",
        "kleos": "#fde047",
    },
    "dracula": {
        "primary": "#bd93f9",      # Purple
        "secondary": "#ff79c6",    # Pink
        "success": "#50fa7b",      # Green
        "warning": "#f1fa8c",      # Yellow
        "error": "#ff5555",        # Red
        "info": "#8be9fd",         # Cyan
        "muted": "#6272a4",        # Comment
        "user": "#f8f8f2",         # Foreground
        "ai": "#bd93f9",
        "border": "#44475a",       # Selection
        "kleos": "#fde047",
    },
    "nord": {
        "primary": "#88c0d0",      # Frost Blue
        "secondary": "#81a1c1",    # Darker Blue
        "success": "#a3be8c",      # Green
        "warning": "#ebcb8b",      # Yellow
        "error": "#bf616a",        # Red
        "info": "#d8dee9",         # Snow
        "muted": "#4c566a",        # Dark Gray
        "user": "#eceff4",         # Snow Blue
        "ai": "#88c0d0",
        "border": "#434c5e",
        "kleos": "#fde047",
    },
    "monokai": {
        "primary": "#f92672",      # Pink
        "secondary": "#a6e22e",    # Green
        "success": "#a6e22e",      # Green
        "warning": "#e6db74",      # Yellow
        "error": "#f92672",        # Pink
        "info": "#66d9ef",         # Blue
        "muted": "#75715e",        # Gray
        "user": "#f8f8f2",         # White
        "ai": "#f92672",
        "border": "#f92672",
        "kleos": "#fde047",
    }
}

# Global COLORS dictionary that components will reference
# Default to "red" theme
COLORS = THEMES["red"].copy()

def apply_theme(theme_name: str):
    """Update the global COLORS dictionary with the selected theme."""
    if theme_name in THEMES:
        COLORS.update(THEMES[theme_name])
        return True
    return False


# =============================================================================
# Header Panel
# =============================================================================

class HeaderPanel:
    """Header component showing app name, model, and status."""
    
    def __init__(
        self, 
        model: str = "gemini-2.5-flash",
        provider: str = "GOOGLE",
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
            display_name = "Kleos"
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
        ("/theme", "Change UI theme (hl3, matrix, etc.)"),
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
        footer.append("/ts", style=f"bold {COLORS['warning']}")
        footer.append(" stats", style=COLORS["muted"])
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
