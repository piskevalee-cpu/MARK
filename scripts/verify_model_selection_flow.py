import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mark_cli.main import MarkApp
from mark_cli.config import load_config

async def test_selection():
    # Force utf-8 output for windows console
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("--- Testing Model Selection Logic ---")
    
    app = MarkApp()
    await app.initialize()
    
    # Mock the console/UI to avoid real input
    # Scenario 1: Select Gemma 3 base model -> Choose Italian
    print("\n[Scenario 1] Selecting 'gemma-3-27b' -> 'it'")
    
    # Simulate /model gemma-3-27b command
    # We patch input() to return 'it'
    with patch('builtins.input', return_value='it'):
        await app._handle_model_command(['gemma-3-27b'])
        
    # Check config
    app.config = load_config() # Reload to be sure
    print(f"  Config Model: {app.config.default_model}")
    print(f"  Config Language: {app.config.language}")
    
    if app.config.default_model == "gemma-3-27b-it" and app.config.language == "it":
        print("  [SUCCESS] Model and language set correctly.")
    else:
        print(f"  [FAIL] Expected gemma-3-27b-it/it, got {app.config.default_model}/{app.config.language}")

    # Scenario 2: Select Gemma 3 base model -> Default English (empty input)
    print("\n[Scenario 2] Selecting 'gemma-3-27b' -> 'en' (default)")
    with patch('builtins.input', return_value=''):
        await app._handle_model_command(['gemma-3-27b'])
        
    app.config = load_config()
    print(f"  Config Model: {app.config.default_model}")
    print(f"  Config Language: {app.config.language}")
    
    if app.config.default_model == "gemma-3-27b-en" and app.config.language == "en":
         print("  [SUCCESS] Model and language defaulted to English.")
    else:
        print(f"  [FAIL] Expected gemma-3-27b-en/en, got {app.config.default_model}/{app.config.language}")

    # Scenario 3: Select normal model (gemini-1.5-flash)
    print("\n[Scenario 3] Selecting 'gemini-1.5-flash'")
    await app._handle_model_command(['gemini-1.5-flash'])
    
    app.config = load_config()
    print(f"  Config Model: {app.config.default_model}")
    
    if app.config.default_model == "gemini-1.5-flash":
         print("  [SUCCESS] Normal model selection worked.")
    else:
         print(f"  [FAIL] Expected gemini-1.5-flash, got {app.config.default_model}")

if __name__ == "__main__":
    asyncio.run(test_selection())
