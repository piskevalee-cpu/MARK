import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mark_cli.config import load_config, get_system_prompt

print("--- Testing Name Injection ---")
test_name = "Valerio"
prompt = get_system_prompt("en", user_name=test_name)

print("Prompt snippet:")
print(prompt[:200])

if test_name in prompt:
    print(f"\n[SUCCESS] User name '{test_name}' found in prompt.")
else:
    print(f"\n[FAIL] User name '{test_name}' NOT found.")

print("\n--- Testing Tone Instructions ---")
if "professional and accurate" in prompt:
    print("[SUCCESS] Found 'professional and accurate'.")
else:
    print("[FAIL] Missing standard professional tone.")
    
if "DO NOT use slang" in prompt:
    print("[SUCCESS] Found 'DO NOT use slang' constraint.")
else:
    print("[FAIL] Missing slang constraint.")
