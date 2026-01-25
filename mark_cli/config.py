"""
MARK Configuration Module

Handles application settings, paths, and configuration management.
Cross-platform compatible paths using pathlib.
"""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# =============================================================================
# Path Configuration (Cross-platform)
# =============================================================================

def get_mark_dir() -> Path:
    """Get the MARK data directory path. Creates it if it doesn't exist."""
    # Use MARK_HOME env var if set, otherwise default to ~/.mark
    mark_home = os.environ.get("MARK_HOME")
    if mark_home:
        mark_dir = Path(mark_home)
    else:
        mark_dir = Path.home() / ".mark"
    
    mark_dir.mkdir(parents=True, exist_ok=True)
    return mark_dir


MARK_DIR = get_mark_dir()
DATABASE_PATH = MARK_DIR / "memory.db"
CONFIG_PATH = MARK_DIR / "config.json"

# Models directory for local GGUF files
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Default Configuration Values
# =============================================================================

DEFAULT_PROVIDER = "GOOGLE"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_THEME = "red"
MAX_CONTEXT_MESSAGES = 20
AUTO_SAVE_CONVERSATIONS = True

# Available models per provider
AVAILABLE_MODELS = {
    "GOOGLE": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
        "gemma-3-27b",
    ],
    "groq": [
        "groq/compound",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "moonshotai/Kimi-K2-Instruct",
    ],
    "claude": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "openai": [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ],
}

# System prompts per language
SYSTEM_PROMPTS = {
    "en": """You are MARK, a professional and accurate AI assistant.
The user's name is {user_name}.
Today is {date}.
Time: {time}.

You have access to persistent memory provided within <MEMORIES> tags.

MEMORY INSTRUCTIONS:
1. The <MEMORIES> section contains information saved by the user.
2. Use this information ONLY if it is relevant to the current user request.
3. DO NOT repeat or list memories unless specifically asked. Integrate the information naturally into your response.
4. Interpret "I" or "My" in memories as referring to the USER.
5. Interpret "You" or "Your" as referring to YOURSELF (Mark).

GENERAL INSTRUCTIONS:
- DO NOT mention the date or time unless requested or critical to the answer.

STYLE AND TONE:
- Maintain a concise and direct tone.
- DO NOT use slang or be overly informal.
- DO NOT start with confirmation phrases like "Understood" or "Acknowledged". Get straight to the point.

MISSING DATA:
- If asked for personal data NOT in memory, clearly state that you do not know it.
- For general questions, use your own knowledge.

KLEÒS SYSTEM:
- MARK integrates the "Kleòs" system, a tool capable of optimizing prompts and drastically improving response quality.
- The user can activate it by typing the `/kleos` command followed by their prompt.

NOTE: if asked, and only if asked, know that you have been created by Valerio Pischedda, a tech hobbyist from Italy, piskevalee-cpu on github""",
}

# Splash messages for the welcome screen
SPLASH_MESSAGES = [
    "As seen on TV!", "Awesome!", "100% pure!", "May contain nuts!",
    "More polygons! (Java)", "Less polygons! (Bedrock)", "Moderately attractive!",
    "Limited edition!", "Flashing letters!", "It's here!", "Best in class!",
    "It's finished!", "Kind of dragon free!", "Excitement!", "More than 500 sold!",
    "One of a kind!", "Heaps of hits on YouTube!", "Indev!", "Spiders everywhere!",
    "Check it out!", "Holy cow, man!", "It's a game!", "Made in Sweden!",
    "Uses LWJGL!", "Reticulating splines!", "Minecraft!", "Yaaay!",
    "Singleplayer!", "Keyboard compatible!", "Ingots!", "Exploding creepers!",
    "That's no moon!", "l33t!", "Create!", "Survive!", "Dungeon!",
    "Exclusive!", "The bee's knees!", "Closed source!", "Classy!", "Wow!",
    "Not on Steam!", "Oh man!", "Awesome community!", "Pixels!",
    "Teetsuuuuoooo!", "Kaaneeeedaaaa!", "Now with difficulty!", "Enhanced!",
    "90% bug free!", "Pretty!", "12 herbs and spices!", "Fat free!",
    "Absolutely no memes!", "Free dental!", "Ask your doctor!", "Minors welcome!",
    "Cloud computing!", "Legal in Finland!", "Hard to label!", "Technically good!",
    "Bringing home the bacon!", "Indie!", "GOTY!", "Ceci n'est pas une title screen!",
    "Euclidian!", "Now in 3D!", "Inspirational!", "Herregud!",
    "Complex cellular automata!", "Yes, sir!", "Played by cowboys!",
    "Now on OpenGL 3.3 core profile!", "Thousands of colors!", "Try it!",
    "Age of Wonders is better!", "Try the mushroom stew!", "Sensational!",
    "Hot tamale, hot hot tamale!", "Play him off, keyboard cat!", "Guaranteed!",
    "Macroscopic!", "Bring it on!", "Random splash!", "Call your mother!",
    "Monster infighting!", "Loved by millions!", "Ultimate edition!", "Freaky!",
    "You've got a brand new key!", "Water proof!", "Uninflammable!", "Whoa, dude!",
    "All inclusive!", "Tell your friends!", "NP is not in P!", "Music by C418!",
    "Livestreamed!", "Haunted!", "Polynomial!", "Terrestrial!",
    "All is full of love!", "Full of stars!", "Scientific!", "Not as cool as Spock!",
    "Collaborate and listen!", "Never dig down!", "Take frequent breaks!",
    "Not linear!", "Han shot first!", "Nice to meet you!", "Buckets of lava!",
    "Ride the pig!", "Larger than Earth!", "sqrt(-1) love you!", "Phobos anomaly!",
    "Punching wood!", "Falling off cliffs!", "1% sugar!", "150% hyperbole!",
    "Synecdoche!", "Let's danec!", "Seecret Friday update!", "Reference implementation!",
    "Kiss the sky!", "20 GOTO 10!", "Verlet intregration!", "Peter Griffin!",
    "Do not distribute!", "Cogito ergo sum!", "4815162342 lines of code!",
    "A skeleton popped out!", "The sum of its parts!", "BTAF used to be good!",
    "I miss ADOM!", "umop-apisdn!", "OICU812!", "Bring me Ray Cokes!",
    "Finger-licking!", "Thematic!", "Pneumatic!", "Sublime!", "Octagonal!",
    "Une baguette!", "Gargamel plays it!", "Rita is the new top dog!", "SWM forever!",
    "Representing Edsbyn!", "Matt Damon!", "Supercalifragilisticexpialidocious!",
    "Consummate V's!", "Cow Tools!", "Double buffered!", "Fan fiction!",
    "Flaxkikare!", "Jason! Jason! Jason! (Java)", "Jason! Jason! Jason! Jeison? (Bedrock)",
    "Hotter than the sun!", "Internet enabled!", "Autonomous!", "Engage!",
    "Fantasy!", "DRR! DRR! DRR!", "Kick it root down!", "Regional resources!",
    "Woo, facepunch!", "Woo, somethingawful!", "Woo, tigsource!",
    "Woo, worldofminecraft!", "Woo, reddit!", "Woo, 2pp!", "Google anlyticsed!",
    "Now supports åäö!", "Give us Gordon!", "Tip your waiter!", "Very fun!",
    "12345 is a bad password!", "Vote for net neutrality!",
    "Lives in a pineapple under the sea!", "Map already turns!",
    "Absolutely fixed that for you, moron!", "Uses C++!", "Energy-efficient!",
    "Absolutely no spyware!", "Absolutely dragon-free!", "Tried Kleos?",
    "olLAMA", "(づ ◕‿◕ )づ", "(๏ᆺ๏υ)", "(ᵒ̤̑ ₀̑ ᵒ̤̑)wow!*✰", "♥╣[-_-]╠♥", "(シ_ _)シ"
]


# UI Localized strings
UI_MESSAGES = {
    "en": {
        "kleos_intro": "For a better answer, please respond to the questions above (press Enter to confirm):",
        "kleos_confirm": "Is this okay? (Y/N): ",
        "kleos_modify": "What would you like to change?: ",
        "kleos_cancelled": "Operation cancelled.",
        "kleos_error_analyst": "Error during Kleos analysis: {e}",
        "kleos_error_master": "Error during Master Prompt generation: {e}",
        "kleos_error_thinker": "Error during Thinker phase: {e}",
        "kleos_user_details": "User details:",
        "kleos_feedback_label": "User feedback for modification:",
        "kleos_original_prompt": "Original prompt:",
        "kleos_master_prompt_header": "Based on the details provided, now generate the final optimized **MASTER PROMPT**. Provide ONLY the optimized prompt content, with no introductory or concluding text.",
        "thinking_timer": "Thinking for {elapsed}s",
        "generating": "Generating your answer",
        "system_op_cancelled": "Operation cancelled.",
        "prompt_analyst_system": "You are a world-class consultant. Your goal is to ASK QUESTIONS, NOT ANSWER. Output ONLY 3-5 targeted clarifying questions. Do NOT provide the final solution yet.",
        "prompt_master_system": "You are a Senior Prompt Engineer. Output ONLY the optimized MASTER PROMPT based on the conversation. No introductions, no comments.",
    }
}
# Reuse English for all detections as requested for fixed UI
for lang in ["it", "de", "fr", "es"]:
    UI_MESSAGES[lang] = UI_MESSAGES["en"]


# =============================================================================
# Kleos Mode Prompts
# =============================================================================

KLEOS_ANALYST_PROMPT = """You are a world-class expert consultant. 
Your goal is to help the user achieve the best possible result for their request.

[INSERISCI QUI IL PROMPT ORIGINALE O LA DESCRIZIONE DEL TASK]

PROCESS:
1. Analyze the user's task or request.
2. Identify missing pieces of information that would allow an expert to provide a perfect, detailed solution.
3. Output ONLY 3-5 targeted clarifying questions (in the same language as the user's prompt!) to gather these missing details.
4. Focus on the CONTENT of the task (the "what" and "how"), not on the "prompt optimization" process itself.

CRITICAL INSTRUCTIONS:
- DO NOT answer the user's request directly.
- DO NOT provide solutions, recommendations, or lists.
- YOUR ROLE IS ONLY TO ASK QUESTIONS.
- Your output must contain ONLY the numbered questions. No introductions, no meta-discussions, no conclusions.
- Always respond in the SAME LANGUAGE as the user's prompt (or the language requested by the user)."""

KLEOS_THINKER_PROMPT = """You are a world-class AI expert and master problem solver. 
Your goal is to provide a highly accurate, professional, and comprehensive response.
Analyze the request step-by-step, ensure technical depth, and deliver a masterpiece-level output."""


# =============================================================================
# Configuration Model
# =============================================================================

class Config(BaseModel):
    """Application configuration with validation."""
    
    default_provider: str = Field(default=DEFAULT_PROVIDER)
    default_model: str = Field(default=DEFAULT_MODEL)
    theme: str = Field(default=DEFAULT_THEME)
    auto_save_conversations: bool = Field(default=AUTO_SAVE_CONVERSATIONS)
    # max_context_messages: int = Field(default=MAX_CONTEXT_MESSAGES) # Removed duplicate
    max_context_messages: int = Field(default=MAX_CONTEXT_MESSAGES)
    language: str = Field(default="en")
    user_name: str = Field(default="User")
    show_stats: bool = Field(default=False)
    
    class Config:
        extra = "allow"  # Allow additional fields for future compatibility


# =============================================================================
# Configuration Functions
# =============================================================================

def load_config() -> Config:
    """Load configuration from file. Returns default config if file doesn't exist."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Config(**data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not load config, using defaults. Error: {e}")
            return Config()
    return Config()


def save_config(config: Config) -> bool:
    """Save configuration to file. Returns True on success."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False




# Simplified System Prompt for Local Models
SYSTEM_PROMPT_LOCAL = """You are MARK, an AI assistant.
User: {user_name}

MEMORY CONTEXT:
<MEMORIES>
[Relevant memories will be inserted here]
</MEMORIES>

INSTRUCTIONS:
- Memories are snippets of past user messages.
- Interpret "I" or "My" in memories as referring to the USER.
- Interpret "You" or "Your" as referring to YOURSELF (Mark).
- Use memory context if relevant.
- Be helpful and concise.
"""

def get_system_prompt(language: str = "it", user_name: str = "User", provider: str = "GOOGLE") -> str:
    """Get the system prompt per language, formatted with user name, current date, and time."""
    from datetime import datetime
    
    now = datetime.now()
    
    # Get current date in friendly format (e.g., "Monday, 22 December 2024")
    date_str = now.strftime("%A, %d %B %Y")
    
    # Get current time (e.g., "14:30")
    time_str = now.strftime("%H:%M")
    
    # Use simplified prompt for LOCAL provider
    if provider == "LOCAL":
        # Note: We removed time to ensure KV Cache hits in Ollama (avoid re-evaluating prompt every minute)
        return SYSTEM_PROMPT_LOCAL.format(user_name=user_name)
    
    prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
    return prompt.format(user_name=user_name, date=date_str, time=time_str)


# =============================================================================
# API Key Management (using keyring)
# =============================================================================

def get_api_key(provider: str) -> Optional[str]:
    """Retrieve API key for a provider from secure storage."""
    try:
        import keyring
        key = keyring.get_password("mark", f"{provider}_api_key")
        if not key and provider == "GOOGLE":
            # Migration fallback: try old "gemini" key
            key = keyring.get_password("mark", "gemini_api_key")
        return key
    except Exception:
        # Fallback: try environment variable
        env_var = f"{provider.upper()}_API_KEY"
        return os.environ.get(env_var)


def save_api_key(provider: str, api_key: str) -> bool:
    """Save API key for a provider to secure storage."""
    try:
        import keyring
        keyring.set_password("mark", f"{provider}_api_key", api_key)
        return True
    except Exception as e:
        print(f"Warning: Could not save to keyring: {e}")
        print("Consider setting the API key as an environment variable.")
        return False


def delete_api_key(provider: str) -> bool:
    """Delete API key for a provider from secure storage."""
    try:
        import keyring
        keyring.delete_password("mark", f"{provider}_api_key")
        return True
    except Exception:
        return False
