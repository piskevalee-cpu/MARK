#!/usr/bin/env python3
"""
MARK - AI Terminal Wrapper

Main entry point for the MARK application.
A universal AI API wrapper with persistent memory and Rich UI.
"""

import asyncio
import sys
import re
from datetime import datetime
from typing import List, Optional

from rich.console import Console

# Local imports
from .config import (
    AVAILABLE_MODELS,
    Config,
    get_api_key,
    get_system_prompt,
    load_config,
    save_api_key,
    save_config,
    MARK_DIR,
)
from .database import MemoryDB, init_database
from .memory import MemoryManager
from .providers import GeminiProvider, GroqProvider
from .providers.base import AIProvider, Message
from .ui import MarkInterface
from .ui.interface import SetupWizard


# =============================================================================
# Application Class
# =============================================================================

class MarkApp:
    """Main MARK application class."""
    
    def __init__(self):
        self.console = Console()
        self.ui = MarkInterface(self.console)
        self.config: Optional[Config] = None
        self.provider: Optional[AIProvider] = None
        self.memory: Optional[MemoryManager] = None
        self.db: Optional[MemoryDB] = None
        self.context: List[Message] = []
        self._running = False
    
    async def initialize(self) -> bool:
        """
        Initialize the application.
        
        Returns:
            True if initialization successful
        """
        # Ensure data directory exists
        MARK_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        init_database()
        self.db = MemoryDB()
        self.memory = MemoryManager(self.db)
        
        # Load or create config
        self.config = load_config()
        
        # Check for API key
        api_key = get_api_key(self.config.default_provider)
        
        if not api_key:
            # Run setup wizard
            return await self._run_setup()
        
        # Initialize provider based on config
        try:
            self.provider = self._create_provider(
                self.config.default_provider,
                api_key,
                self.config.default_model
            )
            
            # Validate API key
            if not await self.provider.validate_api_key():
                self.ui.print_error(
                    "API key invalid or expired.",
                    suggestion="Run /config to update configuration."
                )
                return await self._run_setup()
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Initialization error: {e}")
            return False
    
    def _create_provider(self, provider_name: str, api_key: str, model: str) -> AIProvider:
        """Create the appropriate provider instance based on provider name."""
        if provider_name.lower() == "groq":
            return GroqProvider(api_key=api_key, model=model)
        else:
            # Default to GOOGLE
            return GeminiProvider(api_key=api_key, model=model)
    
    async def _run_setup(self) -> bool:
        """Run the setup wizard."""
        wizard = SetupWizard(self.console)
        setup_config = wizard.run()
        
        if not setup_config:
            return False
        
        # Save API key
        api_key = setup_config.get("api_key")
        provider = setup_config.get("provider", "GOOGLE")
        model = setup_config.get("model", "gemini-2.5-flash")
        
        if api_key:
            save_api_key(provider, api_key)
        
        # Update config
        self.config.default_provider = provider
        self.config.default_model = model
        
        # Save language if provided by wizard
        if "language" in setup_config:
            self.config.language = setup_config["language"]
            
        save_config(self.config)
        
        # Initialize provider using helper
        self.provider = self._create_provider(provider, api_key, model)
        
        # Validate
        self.console.print()
        with self.console.status("[bold purple]Validating API key..."):
            if await self.provider.validate_api_key():
                self.ui.print_system_message(
                    "Setup complete! MARK is ready.",
                    style="success"
                )
                return True
            else:
                self.ui.print_error(
                    "Invalid API key.",
                    suggestion="Check key and try again."
                )
                return False

    
    async def run(self):
        """Main application loop."""
        self._running = True
        
        # Show welcome
        self.ui.print_welcome()
        
        # Print header
        self.ui.print_header(
            model=self.config.default_model,
            provider=self.config.default_provider,
            connected=True
        )
        
        # Print footer hint
        self.ui.print_footer()
        self.console.print()
        
        while self._running:
            try:
                # Get user input
                user_input = self.ui.prompt_input()
                
                if not user_input.strip():
                    continue
                
                # Process input
                await self._process_input(user_input)
                
            except KeyboardInterrupt:
                self.console.print()
                self.ui.print_system_message(
                    "Press Ctrl+C again to exit, or type /quit",
                    style="warning"
                )
                try:
                    user_input = self.ui.prompt_input()
                    if user_input.strip():
                        await self._process_input(user_input)
                except KeyboardInterrupt:
                    self._running = False
            except EOFError:
                self._running = False
        
        # Goodbye
        self.console.print()
        self.ui.print_system_message("Goodbye! 👋", style="info")
    
    async def _process_input(self, user_input: str):
        """Process user input."""
        user_input = user_input.strip()
        
        # Check for commands
        if user_input.startswith("/"):
            await self._handle_command(user_input)
            return
        
        # Check for memory command
        if self.memory.is_memory_command(user_input):
            success, message = self.memory.process_memory_command(user_input)
            self.ui.print_system_message(message, style="success" if success else "warning")
            return
        
        # Regular message - send to AI
        await self._send_to_ai(user_input)
    
    async def _handle_command(self, command: str):
        """Handle slash commands."""
        parts = command.lower().split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in ["/quit", "/exit", "/q"]:
            self._running = False
            
        elif cmd in ["/help", "/h", "/?"]:
            self.ui.print_help()
            
        elif cmd in ["/clear", "/cls"]:
            self.ui.clear()
            self.ui.print_header(
                model=self.config.default_model,
                provider=self.config.default_provider
            )
            
        elif cmd == "/model":
            # Pass the input queue to handle interactive prompts if needed
            # Since self.ui.prompt_input is blocking, we can just use that inside the handler
            await self._handle_model_command(args)
            
        elif cmd == "/stats":
            self._show_stats()
            
        elif cmd == "/memory":
            await self._handle_memory_command(args)
            
        elif cmd == "/reset":
            self.context = []
            if self.provider:
                self.provider.reset_session_usage()
                if hasattr(self.provider, 'reset_chat'):
                    self.provider.reset_chat()
            self.ui.print_system_message("Session reset.", style="success")
            
        elif cmd == "/config":
            await self._run_setup()
        
        elif cmd == "/kleos":
            prompt = " ".join(args).strip()
            if not prompt:
                self.ui.print_system_message("Usage: /kleos <prompt>", "warning")
            else:
                await self._handle_kleos_mode(prompt)
            
        elif cmd in ["/changeusr", "/changename"]:
            new_name = " ".join(args).strip()
            if not new_name:
                self.ui.print_system_message("Usage: /changeusr <new_name>", "warning")
            else:
                self.config.user_name = new_name
                save_config(self.config)
                self.ui.print_system_message(f"User name updated to: {new_name}", "success")
            

        else:
            self.ui.print_system_message(
                f"Unknown command: {cmd}\nUse /help to see commands.",
                style="warning"
            )
    
    async def _handle_model_command(self, args: List[str]):
        """Handle /model command - unified provider/model selection."""
        providers = ["groq", "GOOGLE"]
        
        # STEP 1: Provider Selection
        self.console.print()
        self.console.print("[bold cyan]━━━ SELECT PROVIDER ━━━[/]")
        for i, p in enumerate(providers, 1):
            indicator = "→" if p == self.config.default_provider else " "
            self.console.print(f"  {indicator} [{i}] {p.upper()}")
        
        self.console.print(f"\nChoice (1-{len(providers)}, Enter to keep current): ", end="")
        provider_choice = input().strip()
        
        # Determine selected provider
        if provider_choice:
            try:
                idx = int(provider_choice) - 1
                if 0 <= idx < len(providers):
                    new_provider = providers[idx]
                else:
                    new_provider = self.config.default_provider
            except ValueError:
                new_provider = self.config.default_provider
        else:
            new_provider = self.config.default_provider
        
        # STEP 1b: Check/Get API Key for provider
        api_key = get_api_key(new_provider)
        
        if not api_key:
            self.console.print()
            self.console.print(f"[bold cyan]🔑 API Key Required for {new_provider.upper()}[/]")
            
            if new_provider == "GOOGLE":
                self.console.print("[dim]Get a key from: https://aistudio.google.com/apikey[/]")
            else:
                self.console.print("[dim]Get a key from: https://console.groq.com/keys[/]")
            
            self.console.print("API key: ", end="")
            try:
                import getpass
                api_key = getpass.getpass(prompt="")
            except Exception:
                api_key = input()
            
            if not api_key or len(api_key) < 10:
                self.ui.print_error("Invalid API key. Aborting.")
                return
            
            save_api_key(new_provider, api_key)
            self.ui.print_system_message("API key saved.", "success")
        
        # STEP 2: Model Selection
        available_models = AVAILABLE_MODELS.get(new_provider, [])
        
        self.console.print()
        self.console.print("[bold cyan]━━━ SELECT MODEL ━━━[/]")
        for i, m in enumerate(available_models, 1):
            # Check if this is the current model (handle language suffix)
            is_current = self.config.default_model.startswith(m)
            indicator = "→" if is_current else " "
            self.console.print(f"  {indicator} [{i}] {m}")
        
        self.console.print(f"\nChoice (1-{len(available_models)}, default 1): ", end="")
        model_choice = input().strip()
        
        try:
            idx = int(model_choice) - 1
            if 0 <= idx < len(available_models):
                selected_model = available_models[idx]
            else:
                selected_model = available_models[0]
        except ValueError:
            selected_model = available_models[0]
        
        final_model_name = selected_model
        
        # New: Gemma Language Selection Sub-menu
        if final_model_name == "gemma-3-27b":
            self.console.print()
            self.console.print("[dim]Select Language Variant:[/]")
            languages = [
                ("1", "it", "Italian"),
                ("2", "en", "English"),
                ("3", "es", "Spanish"),
                ("4", "fr", "French"),
                ("5", "de", "German"),
            ]
            for num, code, name in languages:
                self.console.print(f"  [{num}] {name} ({code})")
            
            self.console.print(f"Choice (1-5, default 1 Italian): ", end="")
            lang_choice = input().strip()
            
            lang_map = {"1": "it", "2": "en", "3": "es", "4": "fr", "5": "de"}
            selected_lang = lang_map.get(lang_choice, "it")
            
            # Append language
            final_model_name = f"{final_model_name}-{selected_lang}"
            
            # Crucial: Update global language setting
            self.config.language = selected_lang
            self.console.print(f"[dim]Language set to: {selected_lang}[/]")
        
        # STEP 4: Create/Switch Provider if needed
        provider_changed = new_provider != self.config.default_provider
        
        if provider_changed:
            try:
                new_provider_instance = self._create_provider(new_provider, api_key, final_model_name)
                
                # Validate new provider
                with self.console.status("[bold purple]Validating API key..."):
                    if not await new_provider_instance.validate_api_key():
                        self.ui.print_error(
                            "Invalid API key.",
                            suggestion="Check your API key and try again."
                        )
                        return
                
                # Switch to new provider
                self.provider = new_provider_instance
                self.config.default_provider = new_provider
                
                # Reset provider's internal chat state but keep our context
                if hasattr(self.provider, 'reset_chat'):
                    self.provider.reset_chat()
                    
            except Exception as e:
                self.ui.print_error(f"Failed to switch provider: {e}")
                return
        else:
            # Same provider, just update model
            if self.provider:
                self.provider.set_model(final_model_name)
        
        # STEP 5: Save and confirm
        self.config.default_model = final_model_name
        save_config(self.config)
        
        # Show success message
        context_msg = ""
        if provider_changed and self.context:
            context_msg = f"\nConversation context preserved ({len(self.context)} messages)."
        
        self.console.print()
        self.ui.print_system_message(
            f"Provider: {new_provider.upper()}\n"
            f"Model: {final_model_name}"
            f"{context_msg}",
            style="success"
        )
        
        # Update header
        self.ui.print_header(
            model=final_model_name,
            provider=new_provider
        )

    
    async def _handle_memory_command(self, args: List[str]):
        """Handle /memory command."""
        if not args:
            args = ["list"]
        
        action = args[0]
        
        if action == "list":
            memories = self.memory.list_all(limit=20)
            self.ui.print_memories(memories)
            
        elif action == "search" and len(args) > 1:
            query = " ".join(args[1:])
            results = self.memory.search(query)
            self.ui.print_memories(results)
            
        elif action == "delete" and len(args) > 1:
            try:
                memory_id = int(args[1])
                if self.memory.delete(memory_id):
                    self.ui.print_system_message(
                        f"Memory #{memory_id} deleted.",
                        style="success"
                    )
                else:
                    self.ui.print_error(f"Memory #{memory_id} not found.")
            except ValueError:
                self.ui.print_error("Invalid memory ID.")
                
        elif action == "clear":
            count = self.memory.clear_all()
            self.ui.print_system_message(
                f"Deleted {count} memories.",
                style="warning"
            )
        else:
            self.ui.print_panel(
                "Memory commands:\n\n"
                "  /memory list          - List memories\n"
                "  /memory search <term> - Search memories\n"
                "  /memory delete <id>   - Delete memory\n"
                "  /memory clear         - Delete all",
                title="🧠 Memory Management"
            )
    
    def _show_stats(self):
        """Show detailed statistics."""
        session_stats = {}
        if self.provider:
            usage = self.provider.get_session_usage()
            session_stats = {
                "tokens_input": usage.tokens_input,
                "tokens_output": usage.tokens_output,
                "tokens_total": usage.tokens_total,
                "requests_count": usage.requests_count,
            }
        
        db_stats = self.db.get_usage_stats(
            provider=self.config.default_provider
        ) if self.db else {}
        
        self.ui.print_stats(
            session_stats=session_stats,
            db_stats=db_stats,
            provider=self.config.default_provider,
            model=self.config.default_model
        )
    


    async def _handle_kleos_mode(self, original_prompt: str):
        """Handle the multi-stage Kleos mode logic."""
        from .config import KLEOS_ANALYST_PROMPT, KLEOS_THINKER_PROMPT, UI_MESSAGES
        
        # Language management
        def detect_lang(text: str) -> str:
            lang_keywords = {
                'it': {
                    'il', 'lo', 'la', 'gli', 'le', 'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'che', 'non', 'sono', 
                    'è', 'sono', 'ho', 'ha', 'abbiamo', 'hanno', 'come', 'perché', 'quando', 'chi', 'quale', 'questo', 'quello',
                    'filtro', 'olio', 'macchina', 'casa', 'lavoro', 'fare', 'dire', 'potere', 'volere', 'un', 'una', 'uno'
                },
                'es': {
                    'el', 'la', 'los', 'las', 'de', 'en', 'con', 'por', 'para', 'que', 'no', 'son', 
                    'es', 'tengo', 'tiene', 'tenemos', 'tienen', 'como', 'porque', 'cuando', 'quien', 'cual', 'este', 'ese',
                    'hacer', 'decir', 'poder', 'querer', 'un', 'una', 'uno'
                },
                'fr': {
                    'le', 'la', 'les', 'de', 'en', 'avec', 'par', 'pour', 'est', 'que', 'ne', 'sont',
                    'ai', 'as', 'a', 'avons', 'avez', 'ont', 'comment', 'pourquoi', 'quand', 'qui', 'quel', 'ce', 'cette',
                    'faire', 'dire', 'pouvoir', 'vouloir', 'un', 'une'
                },
                'de': {
                    'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'und', 'ist', 'nicht',
                    'habe', 'hat', 'haben', 'wie', 'warum', 'wann', 'wer', 'welcher', 'dieser', 'jener',
                    'machen', 'sagen', 'können', 'wollen'
                },
            }
            # Look for words length >= 2
            words = set(re.findall(r'\b\w{2,}\b', text.lower()))
            scores = {l: len(words.intersection(kws)) for l, kws in lang_keywords.items()}
            
            # Find the best language, but stick to English if no strong signal
            best_lang = max(scores, key=scores.get)
            if scores[best_lang] > 0:
                return best_lang
            return 'en'
            
        lang = detect_lang(original_prompt)
        locale = UI_MESSAGES.get(lang, UI_MESSAGES["en"])
        
        # 1. Activation UI
        timestamp = datetime.now().strftime("%H:%M")
        
        # Clear raw input
        try:
            sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()
        except:
            pass
            
        self.ui.print_kleos_user_message(original_prompt, self.config.user_name, timestamp)
        
        # 2. Analyst Phase - Initial Analysis (Streaming)
        # 2. Analyst Phase - Initial Analysis (Streaming)
        analyst_prompt = KLEOS_ANALYST_PROMPT.replace("[INSERISCI QUI IL PROMPT ORIGINALE O LA DESCRIZIONE DEL TASK]", original_prompt)
        
        cancel_event = asyncio.Event()
        ai_timestamp = datetime.now().strftime("%H:%M")
        
        lang_names = {
            'it': 'Italian',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }
        target_lang_name = lang_names.get(lang, 'English')
        
        # Use English for system prompts that control fixed AI logic behavior
        try:
            stream = self.provider.stream_message(
                message=analyst_prompt,
                system_prompt=UI_MESSAGES["en"].get("prompt_analyst_system") + f" Respond ONLY in {target_lang_name}.",
            )
            
            analyst_full_output = await self.ui.stream_ai_message(
                stream=stream,
                model="Analyst",
                timestamp=ai_timestamp,
                cancel_event=cancel_event,
                style="kleos",
                language=lang
            )
        except Exception as e:
            self.ui.print_error(UI_MESSAGES["en"].get("kleos_error_analyst").format(e=e))
            return

        # 3. Step B: User Answers
        self.console.print(f"  [bold {self.ui.colors['kleos']}]{UI_MESSAGES['en'].get('kleos_intro')}[/]")
        user_answer = input("  > ").strip()
        user_details = [user_answer] if user_answer else []
        
        # 4. Generate & Refine Master Prompt Loop
        current_context = f"User details: {chr(10).join(user_details)}" if user_details else ""
        final_prompt = None
        
        while True:
            refinement_input = (
                f"Original prompt: '{original_prompt}'\n"
                f"{current_context}\n\n"
                f"Based on the details, generate the optimized MASTER PROMPT in {target_lang_name}. Output ONLY the prompt content."
            )
            
            try:
                stream = self.provider.stream_message(
                    message=refinement_input,
                    system_prompt=UI_MESSAGES["en"].get("prompt_master_system") + f" Respond ONLY in {target_lang_name}.",
                )
                
                final_prompt = await self.ui.stream_ai_message(
                    stream=stream,
                    model="Master Prompt",
                    timestamp=datetime.now().strftime("%H:%M"),
                    cancel_event=cancel_event,
                    style="kleos",
                    language=lang
                )
            except Exception as e:
                self.ui.print_error(UI_MESSAGES["en"].get("kleos_error_master").format(e=e))
                return

            self.console.print(f"  [bold {self.ui.colors['kleos']}]{UI_MESSAGES['en'].get('kleos_confirm')}[/]", end="")
            choice = input().strip().lower()
            
            if choice in ['y', 'yes', '']:
                break
            else:
                self.console.print(f"  [bold {self.ui.colors['info']}]{UI_MESSAGES['en'].get('kleos_modify')}[/]", end="")
                feedback = input().strip()
                if not feedback:
                    self.ui.print_system_message(UI_MESSAGES["en"].get("kleos_cancelled"), "info")
                    return
                current_context += f"\nUser feedback for modification: {feedback}"

        # 5. Thinker Phase (Deep Reasoning)
        
        # Get relevant memories for the final task
        memories = self.memory.get_relevant_memories(final_prompt)
        memories_context = self.memory.format_memories_for_context(memories)
        
        # Send to AI with Thinker system prompt (Streaming)
        ai_timestamp = datetime.now().strftime("%H:%M")
        
        try:
            stream = self.provider.stream_message(
                message=final_prompt,
                context=[], # Clean context for the Master Prompt to avoid refusals
                system_prompt=KLEOS_THINKER_PROMPT,
                memories=memories_context if memories_context else None,
            )
            
            full_content = await self.ui.stream_ai_message(
                stream=stream,
                model="", 
                timestamp=ai_timestamp,
                cancel_event=cancel_event,
                thinking_only=True,
                style="ai",
                language=lang
            )
        except Exception as e:
            self.ui.print_error(locale.get("kleos_error_thinker").format(e=e))
            return

        # 5. Save context
        if full_content:
            self.context.append(Message(role="user", content=original_prompt))
            self.context.append(Message(role="assistant", content=full_content))
            
            if self.config.auto_save_conversations:
                self.db.add_conversation(
                    provider=self.config.default_provider,
                    model=self.config.default_model,
                    user_message=f"[KLEOS] {original_prompt}",
                    ai_response=full_content,
                    tokens_used=0,
                )

    async def _send_to_ai(self, message: str):
        """Send message to AI provider."""
        # Show user message
        timestamp = datetime.now().strftime("%H:%M")
        
        # CLEAR RAW INPUT TRICK: Move cursor up 1 line and clear it
        # This removes the raw text the user just typed, leaving only the rendered panel below
        try:
            sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()
        except:
            pass
            
        self.ui.print_user_message(message, self.config.user_name, timestamp)
        
        # Get relevant memories
        memories = self.memory.get_relevant_memories(message)
        memories_context = self.memory.format_memories_for_context(memories)
        
        # Get system prompt
        # Language is now centrally managed in config.language
        prompt_lang = self.config.language
            
        system_prompt = get_system_prompt(prompt_lang, self.config.user_name)
        
        # New response logic with streaming and cancellation support
        cancel_event = asyncio.Event()
        full_content = ""
        was_cancelled = False
        
        try:
            # First, start the stream (do not await, it returns an async generator)
            stream = self.provider.stream_message(
                message=message,
                context=self.context,
                system_prompt=system_prompt,
                memories=memories_context if memories_context else None,
            )
            
            # Display response with typewriter effect
            # Wrap in a task so we can cancel it
            ai_timestamp = datetime.now().strftime("%H:%M")
            
            # Create a task for the streaming
            async def _stream_with_cancel():
                return await self.ui.stream_ai_message(
                    stream=stream,
                    model=self.config.default_model,
                    timestamp=ai_timestamp,
                    cancel_event=cancel_event
                )
            
            stream_task = asyncio.create_task(_stream_with_cancel())
            
            # Wait for stream with keyboard interrupt handling
            try:
                full_content = await stream_task
            except asyncio.CancelledError:
                was_cancelled = True
                full_content = ""
                
        except KeyboardInterrupt:
            # User pressed Ctrl+C - signal cancellation
            cancel_event.set()
            was_cancelled = True
            self.console.print()  # New line after ^C
            
        except Exception as e:
            self.ui.print_error(
                str(e),
                suggestion="Check connection and try again."
            )
            return
        
        # Only update context and save if we got content
        if full_content:
            # Update context
            self.context.append(Message(role="user", content=message))
            self.context.append(Message(role="assistant", content=full_content))
            
            # Trim context if too long
            max_context = self.config.max_context_messages * 2
            if len(self.context) > max_context:
                self.context = self.context[-max_context:]
            
            # Save conversation
            if self.config.auto_save_conversations:
                self.db.add_conversation(
                    provider=self.config.default_provider,
                    model=self.config.default_model,
                    user_message=message,
                    ai_response=full_content,
                    tokens_used=0,
                )
        
        # Usage update hidden by user request (use /stats to see)


# =============================================================================
# Entry Point
# =============================================================================

async def async_main():
    """Main entry point."""
    app = MarkApp()
    
    # Initialize
    if not await app.initialize():
        print("Initialization failed. Exiting.")
        sys.exit(1)
    
    # Run main loop
    await app.run()


def main():
    """Synchronous wrapper for core script execution."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
