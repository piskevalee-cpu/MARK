
import os
import asyncio
from groq import Groq

# Get API KEY from env or keyring
try:
    import keyring
    API_KEY = keyring.get_password("mark", "groq_api_key")
    if not API_KEY:
        API_KEY = os.environ.get("GROQ_API_KEY")
except:
    API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("No API key found. Please set GROQ_API_KEY env var.")
    exit(1)

client = Groq(api_key=API_KEY)
MODEL = "groq/compound"

async def debug_stream():
    print(f"Testing model: {MODEL}")
    
    messages = [
        {"role": "user", "content": "qual'è il prezzo corrente dello stock nvidia"}
    ]
    
    print("\nSending request...")
    try:
        # Use sync client in async wrapper like the provider does? 
        # Actually the provider uses run_in_executor. We can just use standard iteration for debug script.
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )
        
        print("Stream started. Reading chunks...")
        
        count = 0
        for chunk in stream:
            count += 1
            content = chunk.choices[0].delta.content
            tool_calls = chunk.choices[0].delta.tool_calls
            
            print(f"[{count}] Content: {repr(content)} | ToolCalls: {tool_calls}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # The provider wraps the sync call in thread.
    # Let's just run it simply first.
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(debug_stream())
    except KeyboardInterrupt:
        pass
