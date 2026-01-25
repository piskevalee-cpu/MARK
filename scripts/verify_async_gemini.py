
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mark_cli.config import get_api_key
from google import genai
from google.genai import types

async def main():
    api_key = get_api_key("GOOGLE")
    if not api_key:
        print("No API key found.")
        return

    client = genai.Client(api_key=api_key)
    
    print("Starting ACYNC chat test...")
    
    try:
        # Test Async Chat
        chat = client.aio.chats.create(model="gemini-2.5-flash")
        
        print("Sending message asynchronously...")
        response_stream = await chat.send_message_stream("Count to 5 very quickly.")
        
        print("Iterating stream...")
        async for chunk in response_stream:
            if chunk.text:
                print(f"Chunk: {chunk.text}", end="", flush=True)
        print("\nDone.")
        
    except Exception as e:
        print(f"Async failed: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
