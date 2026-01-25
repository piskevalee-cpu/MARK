"""
MARK Main Interface

The primary Rich-based terminal interface for MARK.
"""

import asyncio
import random
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from .components import (
    COLORS,
    ErrorPanel,
    FooterBar,
    HeaderPanel,
    HelpTable,
    LoadingSpinner,
    MemoryList,
    MessagePanel,
    StatsPanel,
    UsagePanel
)
from .performance import PerformancePanel
from ..config import SPLASH_MESSAGES


class MarkInterface:
    """
    The main Rich-based interface for MARK.
    
    Handles:
    - Console setup and theming
    - Message display and formatting
    - Input prompting
    - Usage stats display
    - Error handling display
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the interface.
        
        Args:
            console: Optional Rich Console instance
        """
        self.console = console or Console()
        
        # UI Components
        self.header = HeaderPanel()
        self.usage = UsagePanel()
        self.colors = COLORS
        
        # State
        self._live: Optional[Live] = None
    
    def clear(self):
        """Clear the terminal screen."""
        self.console.clear()
    
    def print_welcome(self):
        """Print the welcome banner."""
        self.clear()
        
        banner = Text()
        banner.append("\n")
        banner.append("  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗\n", style=f"bold {COLORS['primary']}")
        banner.append("  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝\n", style=f"bold {COLORS['primary']}")
        banner.append("  ██╔████╔██║███████║██████╔╝█████╔╝ \n", style=f"bold {COLORS['primary']}")
        banner.append("  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ \n", style=f"bold {COLORS['secondary']}")
        banner.append("  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗\n", style=f"bold {COLORS['secondary']}")
        banner.append("  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝\n", style=f"bold {COLORS['secondary']}")
        banner.append("\n")
        
        # Pick a random splash message
        splash = random.choice(SPLASH_MESSAGES)
        banner.append(f"  {splash} ", style=f"italic {COLORS['muted']}")
        banner.append(" | ", style=COLORS["muted"])
        banner.append("v1.3.0\n", style=COLORS["info"])
        banner.append("\n")
        
        self.console.print(banner)
    
    def print_header(self, model: str, provider: str, connected: bool = True):
        """Print the header panel."""
        self.header.update(model=model, provider=provider, connected=connected)
        self.console.print(self.header.render())
        self.console.print()
    
    def print_usage(
        self, 
        tokens_used: int = 0,
        requests_count: int = 0,
        rate_limit_ok: bool = True
    ):
        """Print the usage panel."""
        self.usage.update(
            tokens_used=tokens_used,
            requests_count=requests_count,
            rate_limit_ok=rate_limit_ok
        )
        self.console.print(self.usage.render())
    
    def print_performance(
        self,
        tokens_input: int = 0,
        tokens_output: int = 0,
        ttft: float = 0.0,
        context_used: int = 0,
        context_max: int = 0,
        cpu_usage: float = 0.0,
        ram_usage: float = 0.0
    ):
        """Print the performance panel."""
        self.console.print(PerformancePanel.render(
            cpu_usage, ram_usage
        ))
        self.console.print()
        
    def print_response_stats(
        self,
        ttft: float,
        tokens_in: int,
        tokens_out: int,
        total_time: float = 0.0
    ):
        """Print stats below the AI response (Tokens, TTFT, Time)."""
        from rich.text import Text
        
        # Determine colors
        ttft_color = COLORS["success"] if ttft < 1.0 else (COLORS["warning"] if ttft < 3.0 else COLORS["error"])
        
        stats_text = Text()
        stats_text.append("  TTFT: ", style=COLORS["muted"])
        stats_text.append(f"{ttft:.2f}s", style=ttft_color)
        stats_text.append(" | ", style=COLORS["muted"])
        stats_text.append("Tokens: ", style=COLORS["muted"])
        stats_text.append(f"{tokens_in} in / {tokens_out} out", style=COLORS["info"])
        
        if total_time > 0:
            speed = tokens_out / total_time if total_time > 0 else 0
            stats_text.append(" | ", style=COLORS["muted"])
            stats_text.append("Time: ", style=COLORS["muted"])
            stats_text.append(f"{total_time:.2f}s", style=COLORS["info"])
            stats_text.append(" | ", style=COLORS["muted"])
            stats_text.append("Speed: ", style=COLORS["muted"])
            stats_text.append(f"{speed:.1f} t/s", style=COLORS["success"])

        self.console.print(stats_text)
        self.console.print()
    
    def print_user_message(self, content: str, user_name: str = "Utente", timestamp: Optional[str] = None):
        """Print a user message."""
        self.console.print(MessagePanel.user_message(content, user_name, timestamp))
        self.console.print()
    
    def print_kleos_user_message(self, content: str, user_name: str = "Utente", timestamp: Optional[str] = None):
        """Print a Kleos user message with yellow outline."""
        from rich import box
        text = Text()
        text.append(f"{user_name} (Kleos)", style=f"bold {COLORS['kleos']}")
        
        if timestamp:
            text.append(f" | {timestamp}", style=COLORS["muted"])
        
        panel = Panel(
            content,
            title=text,
            title_align="left",
            border_style=COLORS["kleos"],
            padding=(0, 1),
            box=box.ROUNDED
        )
        self.console.print(panel)
        self.console.print()
    
    def print_ai_message(
        self, 
        content: str, 
        model: str = "",
        timestamp: Optional[str] = None
    ):
        """Print an AI response message."""
        self.console.print(MessagePanel.ai_message(content, model, timestamp))
        self.console.print()

    async def stream_ai_message(
        self, 
        stream, 
        model: str = "",
        timestamp: Optional[str] = None,
        cancel_event: Optional[asyncio.Event] = None,
        style: str = "ai",
        final_style: Optional[str] = None,
        final_model: Optional[str] = None,
        thinking_only: bool = False,
        language: str = "en"
    ) -> tuple[str, float]:
        """
        Stream an AI response message with 60FPS-tier fluidity and refined animations.
        
        Returns:
            Tuple of (full_content, time_to_first_token)
        """
        from ..config import UI_MESSAGES
        full_content = ""
        # Brille/Square loader frames
        square_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame_idx = 0
        start_time = asyncio.get_event_loop().time()
        last_update_time = 0
        
        # Performance stats
        ttft = 0.0
        first_token = True
        
        # 60FPS fluid updates (~16.6ms)
        update_interval = 0.016 
        
        # Initial state
        initial_msg = "▌"
        if thinking_only:
            status_text = UI_MESSAGES.get(language, UI_MESSAGES["en"]).get("thinking_timer").format(elapsed=0)
            initial_msg = Text(status_text, style="italic")
        
        with Live(
            MessagePanel.ai_message(initial_msg, model, timestamp, style=style),
            console=self.console,
            refresh_per_second=60, # True 60 FPS target
            auto_refresh=False
        ) as live:
            try:
                async for chunk in stream:
                    # Capture TTFT
                    if first_token:
                        ttft = asyncio.get_event_loop().time() - start_time
                        first_token = False
                    
                    if cancel_event and cancel_event.is_set():
                        full_content += "\n\n*[Response stopped]*"
                        break
                    
                    full_content += chunk
                    now = asyncio.get_event_loop().time()
                    
                    # Update UI on interval
                    if now - last_update_time > update_interval:
                        if thinking_only:
                            # Slower rotation (10 frames per second rotation)
                            slow_frame_idx = int(now * 10) 
                            frame = square_frames[slow_frame_idx % len(square_frames)]
                            
                            elapsed = int(now - start_time)
                            
                            # Force English for fixed UI elements per user request
                            status_text = f"Thinking for {elapsed}s"
                            
                            loader_text = Text()
                            # Yellow loader icon (always yellow for brand consistency)
                            loader_text.append(f"{frame} ", style="bold #fde047")
                            loader_text.append(status_text, style="italic")
                            
                            live.update(MessagePanel.ai_message(
                                loader_text, 
                                model, timestamp, style=style, is_streaming=True
                            ))
                        else:
                            # Live Markdown update with 60FPS pacing
                            live.update(MessagePanel.ai_message(
                                full_content + "▌", 
                                model, timestamp, style=style, is_streaming=True
                            ))
                        live.refresh()
                        last_update_time = now
                    
                    # Ultra-small sleep to keep event loop responsive for 60fps
                    await asyncio.sleep(0.001)
                    
            except Exception:
                pass

            # Final render: use final_style/model if provided
            actual_final_style = final_style or style
            actual_final_model = final_model or model
            live.update(MessagePanel.ai_message(full_content, actual_final_model, timestamp, style=actual_final_style, is_streaming=False))
            live.refresh()
            
        return full_content, ttft
    
    def print_system_message(self, content: str, style: str = "info"):
        """Print a system message."""
        self.console.print(MessagePanel.system_message(content, style))
        self.console.print()
    
    def print_error(
        self, 
        message: str,
        title: str = "Error",
        suggestion: Optional[str] = None
    ):
        """Print an error message."""
        self.console.print(ErrorPanel.render(message, title, suggestion))
        self.console.print()
    
    def print_help(self):
        """Print the help table."""
        self.console.print(HelpTable.render())
        self.console.print()
    
    def print_memories(self, memories: List[Dict[str, Any]]):
        """Print memory list."""
        self.console.print(MemoryList.render(memories))
        self.console.print()
    
    def print_stats(
        self,
        session_stats: Dict[str, Any],
        db_stats: Dict[str, Any],
        provider: str,
        model: str
    ):
        """Print detailed statistics."""
        self.console.print(StatsPanel.render(
            session_stats, db_stats, provider, model
        ))
        self.console.print()
    
    def print_footer(self):
        """Print the footer bar."""
        self.console.print(FooterBar.render())
    
    def prompt_input(self, prompt_text: str = "> ") -> str:
        """
        Prompt for user input.
        
        Args:
            prompt_text: The prompt to display
            
        Returns:
            User input string
        """
        try:
            styled_prompt = Text()
            styled_prompt.append("  ", style="")
            styled_prompt.append(prompt_text, style=f"bold {COLORS['user']}")
            
            return self.console.input(styled_prompt)
        except EOFError:
            return "/quit"
        except KeyboardInterrupt:
            self.console.print()
            return ""
        
    def toggle_stats(self, config):
        """Toggle stats visibility and save."""
        from ..config import save_config
        config.show_stats = not config.show_stats
        save_config(config)
        status = "enabled" if config.show_stats else "disabled"
        self.print_system_message(f"Response statistics {status}.", "success")
    
    def spinner(self, message: str = "Processing...") -> LoadingSpinner:
        """Get a loading spinner context manager."""
        return LoadingSpinner(message)
    
    def print_panel(self, content: str, title: str = "", style: str = "info"):
        """Print a generic panel."""
        self.console.print(Panel(
            content,
            title=title,
            title_align="left",
            border_style=COLORS.get(style, COLORS["info"]),
        ))
        self.console.print()


# =============================================================================
# Setup Wizard Interface
# =============================================================================

class SetupWizard:
    """Interactive setup wizard for first-time configuration."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def run(self) -> Dict[str, Any]:
        """
        Run the setup wizard.
        
        Returns:
            Configuration dictionary with user selections
        """
        self.console.clear()
        
        # Welcome
        self.console.print()
        self.console.print(Panel(
            "Welcome to MARK! 🎉\n\n"
            "Let's configure the application together.",
            title="🚀 Initial Setup",
            title_align="left",
            border_style=COLORS["primary"],
        ))
        self.console.print()
        
        config = {}
        
        # User Name
        self.console.print(Text(
            "USER NAME",
            style=f"bold {COLORS['secondary']}"
        ))
        
        user_name = Prompt.ask(
            Text("   What should I call you?", style=COLORS["info"]),
            default="User",
            console=self.console
        )
        config["user_name"] = user_name
        self.console.print(Text(
            f"   [OK] Hi, {user_name}!\n",
            style=COLORS["success"]
        ))
        
        # Default values for first-time setup
        config["provider"] = "NONE"
        config["model"] = "no model"
        config["api_key"] = ""
        config["language"] = "en"
        
        # Confirmation
        self.console.print(Panel(
            f"Hi {config['user_name']}, setup complete!\n\n"
            f"MARK is starting without an AI model.\n"
            f"You can configure one anytime using the [bold cyan]/model[/] command.",
            title="✅ Configuration Ready",
            title_align="left",
            border_style=COLORS["success"],
        ))
        
        return config
