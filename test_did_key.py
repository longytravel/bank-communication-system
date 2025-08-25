"""
Test if D-ID API key is valid
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("TESTING D-ID API KEY")
print("=" * 60)

api_key = os.getenv('DID_API_KEY')

if not api_key:
    print("❌ No DID_API_KEY found in .env file")
    print("\nTo get a D-ID API key:")
    print("1. Go to https://www.d-id.com/")
    print("2. Sign up for a free account")
    print("3. Go to API Keys section")
    print("4. Create a new API key")
    print("5. Add to .env file: DID_API_KEY=your-key-here")
else:
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test the API key
    headers = {
        "Authorization": f"Basic {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try to get credit balance
    print("\nTesting API connection...")
    try:
        response = requests.get(
            "https://api.d-id.com/credits",
            headers=headers
        )
        
        if response.status_code == 200:
            credits = response.json()
            print(f"✅ API key is valid!")
            print(f"   Credits remaining: {credits.get('remaining', 'Unknown')}")
            print(f"   Credits used: {credits.get('used', 'Unknown')}")
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
            print("   Please check your D-ID API key")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

print("=" * 60)