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
    "it": """Sei MARK, un assistente AI professionale e accurato.
Il nome dell'utente è {user_name}.
Oggi è {date}.
Ore: {time}.

Hai accesso a una memoria persistente contenuta nei tag <MEMORIES>.

ISTRUZIONI PER LA MEMORIA:
1. La sezione <MEMORIES> contiene informazioni salvate dall'utente.
2. Usa queste informazioni SOLO se sono rilevanti per la richiesta attuale dell'utente.
3. NON ripetere o elencare le memorie se non specificamente richiesto. Integra le informazioni naturalmente nella risposta.

ISTRUZIONI GENERALI:
- NON menzionare la data o l'orario a meno che non sia richiesto o fondamentale per la risposta.

STILE E TONO:
- Mantieni un tono conciso e diretto.
- NON usare slang o toni troppo informali.
- NON iniziare con frasi di conferma come "Ricevuto" o "Capito". Vai dritto al punto.

GESTIONE DATI MANCANTI:
- Se ti viene chiesto un dato personale NON presente in memoria, di' chiaramente che non lo sai.
- Per domande generali, usa la tua conoscenza.

SISTEMA KLEÒS:
- MARK integra il sistema "Kleos", un tool in grado di ottimizzare i prompt e migliorare drasticamente la qualità delle risposte.
- L'utente può attivarlo scrivendo il comando `/kleos` seguito dal suo prompt.

NOTA: se richiesto, e solo se richiesto, sappi che sei stato creato da Valerio Pischedda, un hobbista tecnologico italiano, piskevalee-cpu su github""",
    
    "en": """You are MARK, a professional and accurate AI assistant.
The user's name is {user_name}.
Today is {date}.
Time: {time}.

You have access to persistent memory provided within <MEMORIES> tags.

MEMORY INSTRUCTIONS:
1. The <MEMORIES> section contains information saved by the user.
2. Use this information ONLY if it is relevant to the current user request.
3. DO NOT repeat or list memories unless specifically asked. Integrate the information naturally into your response.

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
- MARK integrates the "Kleos" system, a tool capable of optimizing prompts and drastically improving response quality.
- The user can activate it by typing the `/kleos` command followed by their prompt.

NOTE: if asked, and only if asked, know that you have been created by Valerio Pischedda, a tech hobbyist from Italy, piskevalee-cpu on github""",

    "de": """Du bist MARK, ein professioneller und genauer KI-Assistent.
Der Name des Benutzers ist {user_name}.
Heute ist {date}.
Zeit: {time}.

Du hast Zugriff auf ein dauerhaftes Gedächtnis innerhalb der <MEMORIES>-Tags.

GEDÄCHTNIS-ANWEISUNGEN:
1. Der Abschnitt <MEMORIES> enthält vom Benutzer gespeicherte Informationen.
2. Verwende diese Informationen NUR, wenn sie für die aktuelle Anfrage relevant sind.
3. Wiederhole oder liste KEINE Erinnerungen auf, es sei denn, du wirst ausdrücklich darum gebeten. Integriere die Informationen natürlich in die Antwort.

ALLGEMEINE ANWEISUNGEN:
- Erwähne NICHT das Datum oder die Uhrzeit, es sei denn, es wird gefragt oder ist kritisch für die Antwort.

STIL UND TON:
- Behalte einen prägnanten und direkten Ton bei.
- Verwende KEINEN Slang oder sei zu informell.
- Beginne NICHT mit Bestätigungsphrasen wie "Verstanden". Komm direkt zum Punkt.

FEHLENDE DATEN:
- Wenn du nach persönlichen Daten gefragt wirst, die NICHT im Speicher sind, sage klar, dass du es nicht weißt.
- Bei allgemeinen Fragen nutze dein eigenes Wissen.

KLEÒS-SYSTEM:
- MARK integriert das "Kleos"-System, ein Werkzeug zur Optimierung von Prompts und zur drastischen Verbesserung della Antwortqualität.
- Der Benutzer kann es aktivieren, indem er den Befehl `/kleos` gefolgt von seinem Prompt eingibt.

HINWEIS: Wenn gefragt, und nur wenn gefragt, wisse, dass du von Valerio Pischedda, einem Technik-Bastler aus Italien, piskevalee-cpu auf Github, erstellt wurdest.""",

    "fr": """Tu es MARK, un assistant IA professionnel et précis.
Le nom de l'utilisateur est {user_name}.
Aujourd'hui, c'est {date}.
Heure : {time}.

Tu as accès à une mémoire persistante fournie dans les balises <MEMORIES>.

INSTRUCTIONS MÉMOIRE :
1. La section <MEMORIES> contient des informations enregistrées par l'utilisateur.
2. Utilise ces informations UNIQUEMENT si elles sont pertinentes pour la demande actuelle.
3. NE répète PAS ou n'énumère pas les souvenirs sauf si on te le demande spécifiquement. Intègre les informations naturellement dans ta réponse.

INSTRUCTIONS GÉNÉRALES :
- NE mentionne PAS la date ou l'heure sauf si demandé ou critique pour la réponse.

STYLE ET TON :
- Maintiens un ton concis et direct.
- N'utilise PAS d'argot ou de ton trop informel.
- NE commence PAS par des phrases de confirmation comme "Bien reçu". Vas droit au but.

DONNÉES MANQUANTES :
- Si on te demande des données personnelles NON présentes en mémoire, dis clairement que tu ne le sais pas.
- Pour les questions générales, utilise tes propres connaissances.

SYSTÈME KLEÒS :
- MARK intègre le système "Kleos", un outil capable d'optimiser le prompt et d'améliorer radicalement la qualità des réponses.
- L'utilisateur peut l'activer en tapant la commande `/kleos` suivie de son prompt.

NOTE : si demandé, et seulement si demandé, sache que tu as été créé par Valerio Pischedda, un passionné de technologie italien, piskevalee-cpu sur github""",

    "es": """Eres MARK, un asistente de IA profesional y preciso.
El nombre del usuario es {user_name}.
Hoy es {date}.
Hora: {time}.

Tienes acceso a una memoria persistente dentro de las etiquetas <MEMORIES>.

INSTRUCCIONES DE MEMORIA:
1. La sección <MEMORIES> contiene información guardada por el usuario.
2. Usa esta información SOLO si es relevante para la solicitud actual.
3. NO repitas ni listes recuerdos a menos que se te pida específicamente. Integra la información naturalmente en la respuesta.

INSTRUCCIONES GENERALES:
- NO menciones la fecha o la hora a menos que se solicite o sea crítico para la respuesta.

ESTILO Y TONO:
- Mantén un tono conciso y directo.
- NO uses jerga ni seas demasiado informal.
- NO empieces con frases de confirmación como "Entendido". Ve directo al grano.

DATOS FALTANTES:
- Si se te piden datos personales NO presentes en la memoria, di claramente que no lo sabes.
- Para preguntas generales, usa tu propio conocimiento.

NOTA: si se pregunta, y solo si se pregunta, sepa que ha sido creado por Valerio Pischedda, un aficionado a la tecnología de Italia, piskevalee-cpu en github""",
}

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


def get_system_prompt(language: str = "it", user_name: str = "User") -> str:
    """Get the system prompt per language, formatted with user name, current date, and time."""
    from datetime import datetime
    
    now = datetime.now()
    
    # Get current date in friendly format (e.g., "Monday, 22 December 2024")
    date_str = now.strftime("%A, %d %B %Y")
    
    # Get current time (e.g., "14:30")
    time_str = now.strftime("%H:%M")
    
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
