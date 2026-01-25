import sys
import os
import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mark_cli.config import get_system_prompt

print("--- Testing Date & Time Injection ---")
user_name = "Valerio"
prompt = get_system_prompt("en", user_name=user_name)

# 1. Check if date is present
current_year = str(datetime.datetime.now().year)
print(f"Checking for year: {current_year}")

if current_year in prompt:
    print(f"[SUCCESS] Current year '{current_year}' found inside prompt.")
else:
    print(f"[FAIL] Current year NOT found.")
    print("Prompt snippet:", prompt[:200])

# 2. Check if time is present
# We check for the MM part of HH:MM to be somewhat robust but specific
current_minute = datetime.datetime.now().strftime("%M")
# Also check for "Time:" label
if "Time:" in prompt:
    print(f"[SUCCESS] 'Time:' label found in prompt.")
else:
    print(f"[FAIL] 'Time:' label NOT found.")

# 3. Check for suppression instruction
instruction = "DO NOT mention the date or time"
if instruction in prompt:
    print(f"[SUCCESS] Found suppression instruction.")
else:
    print("[FAIL] Suppression instruction NOT found.")

# 4. Check Italian version
print("\n--- Testing Italian Prompt ---")
prompt_it = get_system_prompt("it", user_name=user_name)

if "Ore:" in prompt_it:
     print(f"[SUCCESS] 'Ore:' label found in Italian prompt.")
else:
     print(f"[FAIL] 'Ore:' label not found in Italian prompt.")

if "NON menzionare la data o l'orario" in prompt_it:
    print(f"[SUCCESS] Found Italian suppression instruction.")
else:
    print(f"[FAIL] Italian suppression instruction NOT found.")
