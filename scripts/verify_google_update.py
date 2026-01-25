import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Add project root to path with priority
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mark_cli.config import load_config, DEFAULT_PROVIDER, AVAILABLE_MODELS, get_api_key
from mark_cli.providers.gemini import GeminiProvider

async def verify_updates():
    print("--- Verifying Google Provider and Model Updates ---")
    
    # 1. Verify config defaults
    print(f"\n[1] Verifying config defaults...")
    config = load_config()
    print(f"    Default Provider: {DEFAULT_PROVIDER}")
    print(f"    Supported Models: {AVAILABLE_MODELS.get('GOOGLE')}")
    
    if DEFAULT_PROVIDER == "GOOGLE" and "gemini" not in AVAILABLE_MODELS:
        print("    [SUCCESS] Config updated correctly.")
    else:
        print("    [FAIL] Config check failed.")

    # 2. Verify GeminiProvider property
    print(f"\n[2] Verifying GeminiProvider properties...")
    provider = GeminiProvider(api_key="mock_key")
    print(f"    Provider Name: {provider.provider_name}")
    print(f"    Available Models: {provider.available_models}")
    
    if provider.provider_name == "GOOGLE" and len(provider.available_models) == 4:
        print("    [SUCCESS] Provider class updated correctly.")
    else:
        print("    [FAIL] Provider class check failed.")

    # 3. Verify API key migration logic
    print(f"\n[3] Verifying API key migration logic...")
    with patch('keyring.get_password') as mock_keyring:
        def side_effect(service, name):
            if name == "GOOGLE_api_key": return None
            if name == "gemini_api_key": return "migrated_key_123"
            return None
        
        mock_keyring.side_effect = side_effect
        
        key = get_api_key("GOOGLE")
        print(f"    Retrieved key for GOOGLE: {key}")
        
        if key == "migrated_key_123":
            print("    [SUCCESS] API key migration logic working.")
        else:
            print("    [FAIL] API key migration logic failed.")

if __name__ == "__main__":
    asyncio.run(verify_updates())
