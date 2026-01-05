import sys
import os
import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mark_cli.config import get_system_prompt

languages = {
    "en": "English",
    "it": "Italiano",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español"
}

user_name = "TestUser"
current_year = str(datetime.datetime.now().year)

print(f"--- Testing System Prompts for {len(languages)} Languages ---")

for lang_code, lang_name in languages.items():
    print(f"\nTesting {lang_name} ({lang_code})...")
    prompt = get_system_prompt(lang_code, user_name=user_name)
    
    # Check for basic content
    if user_name in prompt:
        print("  [OK] User name found")
    else:
        print("  [FAIL] User name NOT found")

    # Check for date injection
    if current_year in prompt:
        print("  [OK] Current year found")
    else:
        print("  [FAIL] Current year NOT found")
        
    # Check for time injection (looking for "Ore:" or "Time:" or "Zeit:" or "Heure :" or "Hora:")
    time_labels = ["Time:", "Ore:", "Zeit:", "Heure :", "Hora:"]
    found_label = False
    for label in time_labels:
        if label in prompt:
            found_label = True
            break
            
    if found_label:
        print("  [OK] Time label found")
    else:
        print("  [FAIL] Time label NOT found")

    # Check for specific language indicators
    indicators = {
        "en": "You are MARK",
        "it": "Sei MARK",
        "de": "Du bist MARK",
        "fr": "Tu es MARK",
        "es": "Eres MARK"
    }
    
    expected = indicators.get(lang_code)
    if expected and expected in prompt:
        print(f"  [OK] Correct language indicator '{expected}' found")
    else:
        print(f"  [FAIL] Indicator '{expected}' NOT found in prompt")
        
print("\n--- Test Complete ---")
