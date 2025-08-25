import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Claude connection...")
print("-" * 40)

# Check if API key exists
api_key = os.getenv('CLAUDE_API_KEY')
if api_key:
    print(f"API key found: {api_key[:20]}...")
    
    # Try to connect
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Try a simple test with correct model name
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print("SUCCESS! Claude is working!")
        
    except Exception as e:
        print(f"ERROR: {e}")
else:
    print("ERROR: No API key found")