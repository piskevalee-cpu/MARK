
import os
import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mark_cli.config import get_api_key
from google import genai

async def main():
    api_key = get_api_key("GOOGLE")
    if not api_key:
        print("No API key found for GOOGLE.")
        return

    client = genai.Client(api_key=api_key)
    
    print("Listing models matching 'gemma'...")
    try:
        # Pager through models
        count = 0
        for model in client.models.list():
            if "gemma" in model.name.lower():
                print(f"- {model.name} ({model.display_name})")
                count += 1
            if "gemini" in model.name.lower() and "flash" in model.name.lower():
                 print(f"- {model.name} ({model.display_name})")
                 count += 1
        
        if count == 0:
            print("No matching models found.")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(main())
