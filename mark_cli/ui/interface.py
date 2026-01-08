"""
MARK Main Interface

The primary Rich-based terminal interface for MARK.
"""

import asyncio
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
        banner.append("  ██╔████╔██║███████║██████╔╝█████╔╝ \n", style=f"bold {COLORS['secondary']}")
        banner.append("  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ \n", style=f"bold {COLORS['secondary']}")
        banner.append("  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗\n", style=f"bold {COLORS['ai']}")
        banner.append("  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝\n", style=f"bold {COLORS['ai']}")
        banner.append("\n")
        banner.append("  Now with Kleos system! ", style=f"italic {COLORS['muted']}")
        banner.append(" | ", style=COLORS["muted"])
        banner.append("v1.1.1\n", style=COLORS["info"])
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
    ) -> str:
        """
        Stream an AI response message with 60FPS-tier fluidity and refined animations.
        """
        from ..config import UI_MESSAGES
        full_content = ""
        # Brille/Square loader frames
        square_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame_idx = 0
        start_time = asyncio.get_event_loop().time()
        last_update_time = 0
        
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
            
        return full_content
    
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
        
        # Provider selection
        self.console.print(Text(
            "AI PROVIDER",
            style=f"bold {COLORS['secondary']}"
        ))
        self.console.print(Text(
            "   [1] Groq - Fast inference (GPT-OSS, Llama, Kimi K2)",
            style=COLORS["info"]
        ))
        self.console.print(Text(
            "   [2] GOOGLE - Gemini & Gemma models",
            style=COLORS["info"]
        ))
        
        provider_choice = Prompt.ask(
            Text("   Choose (1-2)", style=COLORS["info"]),
            default="1",
            console=self.console
        )
        
        provider = "groq" if provider_choice == "1" else "GOOGLE"
        config["provider"] = provider
        self.console.print(Text(
            f"   [OK] Selected: {provider.upper()}\n",
            style=COLORS["success"]
        ))
        
        # API Key - provider-specific prompt
        self.console.print(Text(
            "🔑 API Key",
            style=f"bold {COLORS['secondary']}"
        ))
        
        if provider == "GOOGLE":
            self.console.print(Text(
                "   Get a key from: https://aistudio.google.com/apikey",
                style=COLORS["muted"]
            ))
            key_prompt = "   Enter your Google API key: "
        else:
            self.console.print(Text(
                "   Get a key from: https://console.groq.com/keys",
                style=COLORS["muted"]
            ))
            key_prompt = "   Enter your Groq API key: "
        
        while True:
            self.console.print(Text(key_prompt, style=COLORS["info"]), end="")
            try:
                import getpass
                api_key = getpass.getpass(prompt="")
            except Exception:
                api_key = input()
            
            if api_key and len(api_key) > 10:
                config["api_key"] = api_key
                self.console.print(Text(
                    "   ✓ API key saved\n",
                    style=COLORS["success"]
                ))
                break
            else:
                self.console.print(Text(
                    "   ✗ Invalid API key, please try again",
                    style=COLORS["error"]
                ))
        
        # Model selection - provider-specific
        self.console.print(Text(
            "🤖 Model",
            style=f"bold {COLORS['secondary']}"
        ))
        
        if provider == "GOOGLE":
            models = [
                ("1", "gemini-2.5-flash", ""),
                ("2", "gemini-2.5-flash-lite", ""),
                ("3", "gemini-3-flash-preview", ""),
                ("4", "gemma-3-27b", ""),
            ]
            model_map = {
                "1": "gemini-2.5-flash", 
                "2": "gemini-2.5-flash-lite", 
                "3": "gemini-3-flash-preview",
                "4": "gemma-3-27b",
            }
            max_choice = 4
        else:  # groq
            models = [
                ("1", "groq/compound", "Groq Compound - Web Search & Tools"),
                ("2", "llama-3.3-70b-versatile", "Llama 70B - Fast & versatile"),
                ("3", "openai/gpt-oss-120b", "GPT-OSS 120B - High capability"),
                ("4", "moonshotai/Kimi-K2-Instruct", "Kimi K2 - Coding & reasoning"),
            ]
            model_map = {
                "1": "groq/compound",
                "2": "llama-3.3-70b-versatile",
                "3": "openai/gpt-oss-120b", 
                "4": "moonshotai/Kimi-K2-Instruct",
            }
            max_choice = 4
        
        for num, model, desc in models:
            self.console.print(Text(
                f"   [{num}] {model}",
                style=COLORS["info"]
            ) + Text(f" - {desc}", style=COLORS["muted"]))
        
        choice = Prompt.ask(
            Text(f"   Choose (1-{max_choice})", style=COLORS["info"]),
            default="1",
            console=self.console
        )
        
        selected_model = model_map.get(choice, list(model_map.values())[0])
        config["language"] = "en"  # Default

        # Gemma Language Selection Sub-menu
        if selected_model == "gemma-3-27b":
            self.console.print(Text("   Select Language Variant:", style=COLORS["info"]))
            languages = [
                ("1", "it", "Italian"),
                ("2", "en", "English"),
                ("3", "es", "Spanish"),
                ("4", "fr", "French"),
                ("5", "de", "German"),
            ]
            
            for num, code, name in languages:
                self.console.print(Text(f"     [{num}] {name} ({code})", style=COLORS["info"]))
            
            lang_choice = Prompt.ask(
                Text("     Choose (1-5)", style=COLORS["info"]),
                default="1",
                console=self.console
            )
            
            lang_map = {"1": "it", "2": "en", "3": "es", "4": "fr", "5": "de"}
            selected_lang = lang_map.get(lang_choice, "en")
            
            # Update model name and config language
            selected_model = f"gemma-3-27b-{selected_lang}"
            config["language"] = selected_lang
        
        config["model"] = selected_model
        
        self.console.print(Text(
            f"   ✓ Selected Model: {config['model']}\n",
            style=COLORS["success"]
        ))
        
        # Confirmation
        self.console.print(Panel(
            f"Provider: {config['provider'].upper()}\n"
            f"Model: {config['model']}\n"
            f"API Key: {'*' * 20}...{api_key[-4:]}",
            title="✅ Configuration Verified",
            title_align="left",
            border_style=COLORS["success"],
        ))
        
        return config
    
    def validate_api_key_ui(
        self, 
        validate_func: Callable[[], bool]
    ) -> bool:
        """
        Validate API key with visual feedback.
        
        Args:
            validate_func: Async function to validate the key
            
        Returns:
            True if valid
        """
        self.console.print()
        with self.console.status(
            "[bold purple]Validating API key...",
            spinner="dots"
        ):
            try:
                loop = asyncio.get_event_loop()
                is_valid = loop.run_until_complete(validate_func())
                
                if is_valid:
                    self.console.print(Text(
                        "✓ API key valid!",
                        style=f"bold {COLORS['success']}"
                    ))
                    return True
                else:
                    self.console.print(Text(
                        "✗ Invalid API key. Check and try again.",
                        style=f"bold {COLORS['error']}"
                    ))
                    return False
            except Exception as e:
                self.console.print(Text(
                    f"✗ Validation error: {e}",
                    style=f"bold {COLORS['error']}"
                ))
                return False
