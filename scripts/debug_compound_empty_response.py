
import asyncio
import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Load env from .env file (assuming it's in a parent dir or current)
# If running fro scripts/, .env might be in ..
# For simplicity, let's assume MARK setup
# We will use the proper way to get the key from mark_cli if possible, 
# or just expect GROQ_API_KEY env var which the user might have set.
# Actually, the user's app uses keyring. 
# Let's try to load from mark_cli config to be safe.

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mark_cli.config import get_api_key, get_system_prompt
import datetime

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def debug_compound():
    api_key = get_api_key("groq")
    if not api_key:
        print("No API key found for Groq.")
        return

    client = Groq(api_key=api_key)
    
    # Failing query
    prompt = "qual'è l'ultima versione di macos rilasciata?"
    
    # Get System Prompt
    system_prompt = get_system_prompt("en", "Valerio")
    # Add date/time manual injection if get_system_prompt needs it or does it internally?
    # get_system_prompt does it internally with {date} format.
    
    print(f"System Prompt Length: {len(system_prompt)}")
    print(f"Sending Query (STREAMING) with System Prompt...")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        stream = client.chat.completions.create(
            model="groq/compound",
            messages=messages,
            temperature=0.7,
            max_tokens=8192,
            stream=True
        )
        
        print("\n--- STREAM CHUNKS ---\n")
        full_content = ""
        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                # print(f"Chunk: {delta}") 
                if delta.content:
                    print(delta.content, end="", flush=True)
                    full_content += delta.content
                else:
                    # Capture if we get chunks with no content (maybe tool calls or usage)
                    pass
                    # print(f"[No Content Chunk: {chunk}]")
        
        print("\n\n--- FINAL CONTENT ---\n")
        print(full_content)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_compound())
