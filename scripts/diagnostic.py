"""
MARK Diagnostic Script

Run this to debug Gemini API access issues.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from mark_cli.config import get_api_key

def run_diagnostic():
    print("🔍 MARK Diagnostic Tool")
    print("=======================")
    
    # 1. Check API Key
    api_key = get_api_key("gemini")
    if not api_key:
        print("❌ No API Key found in keyring or environment.")
        # Try manual input
        api_key = input("Enter your Gemini API Key manually: ").strip()
        if not api_key:
            return
            
    print(f"✅ API Key found (starts with: {api_key[:4]}...)")
    
    # 2. Configure SDK
    try:
        genai.configure(api_key=api_key)
        print("✅ SDK secure authentication configured")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return

    # 3. List Models
    print("\n📋 Listing Available Models...")
    try:
        models = list(genai.list_models())
        chat_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
        
        if not chat_models:
            print("⚠️ No chat models found available for your API key.")
            print("   This might indicate a regional restriction or API not enabled.")
        else:
            print(f"✅ Found {len(chat_models)} chat models:")
            for m in chat_models:
                print(f"   - {m.name} ({m.display_name})")
                
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return

    # 4. Test Generation
    print("\n🧪 Testing Generation...")
    
    test_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-2.0-flash-exp"
    ]
    
    # Add available models found above to the test list if not present
    for m in chat_models:
        name_only = m.name.replace("models/", "")
        if name_only not in test_models:
            test_models.append(name_only)
            
    for model_name in test_models:
        print(f"\n   Trying model: {model_name}...", end=" ")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, reply with 'OK'.")
            if response.text:
                print(f"✅ SUCCESS! Response: {response.text.strip()}")
                print(f"   >>> RECOMMENDATION: Use '{model_name}' in MARK config.")
                break # Stop after first success
        except Exception as e:
            print(f"❌ FAILED")
            # print(f"      Error: {str(e)[:100]}...") # Cleaned up for move
            print(f"      Error: {str(e)}")

if __name__ == "__main__":
    run_diagnostic()
