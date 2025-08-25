"""
Create a debug script to trace the exact issue
Save this as: debug_voice_issue.py
"""

import sys
sys.path.append('src')
import streamlit as st

# Force reload to see what's in session state
if 'all_customer_plans' in st.session_state:
    plans = st.session_state.all_customer_plans
    
    # Find Maria's plan
    maria_plan = None
    for plan in plans:
        if 'Maria' in plan.get('customer_name', ''):
            maria_plan = plan
            break
    
    if maria_plan:
        print("=" * 60)
        print("MARIA'S PLAN DATA:")
        print("=" * 60)
        print(f"Customer: {maria_plan.get('customer_name')}")
        print(f"Language: {maria_plan.get('customer_language', 'NOT SET')}")
        print(f"Channels: {maria_plan.get('channels')}")
        
        print("\n" + "=" * 60)
        print("MARIA'S CONTENT:")
        print("=" * 60)
        
        content = maria_plan.get('content', {})
        
        # Check all text content
        if 'voice_note' in content:
            voice_content = content['voice_note']
            if isinstance(voice_content, dict):
                print(f"Voice note script: {voice_content.get('script', 'NO SCRIPT')[:200]}")
            else:
                print(f"Voice note text: {voice_content[:200]}")
        
        if 'in_app' in content:
            in_app = content['in_app']
            if isinstance(in_app, dict):
                print(f"In-app message: {in_app.get('message_body', 'NO BODY')[:200]}")
            else:
                print(f"In-app text: {in_app[:200]}")
        
        if 'sms' in content:
            sms = content['sms']
            if isinstance(sms, dict):
                print(f"SMS text: {sms.get('text', 'NO TEXT')[:200]}")
            else:
                print(f"SMS: {sms[:200]}")
        
        # Check what assets exist
        if 'assets' in maria_plan:
            print("\n" + "=" * 60)
            print("MARIA'S ASSETS (if any):")
            print("=" * 60)
            assets = maria_plan['assets']
            for key, value in assets.items():
                if 'voice' in key.lower():
                    print(f"{key}: {str(value)[:200]}")
    else:
        print("Maria's plan not found!")
else:
    print("No plans in session state! Generate plans first.")

# Now let's test direct voice generation with Maria's actual data
print("\n" + "=" * 60)
print("TESTING DIRECT VOICE GENERATION:")
print("=" * 60)

from api.api_manager import APIManager

spanish_text = "Hola María, soy Ana de Resonance Bank. Hemos preparado una selección de servicios premium perfectos para tu perfil financiero."
english_text = "Hello Maria, this is Ana from Resonance Bank. We have prepared a selection of premium services perfect for your financial profile."

api_manager = APIManager()

# Test 1: Generate with Spanish text and Spanish language
print("\n1. Spanish text with Spanish language:")
result1 = api_manager.openai.generate_voice_note(
    spanish_text,
    "DEBUG_SPANISH",
    "notification",
    customer_language="Spanish"
)
print(f"   Generated: {result1}")

# Test 2: Generate with English text
print("\n2. English text (for comparison):")
result2 = api_manager.openai.generate_voice_note(
    english_text,
    "DEBUG_ENGLISH",
    "notification",
    customer_language="English"
)
print(f"   Generated: {result2}")

print("\n" + "=" * 60)
print("LISTEN TO BOTH FILES:")
print("1. DEBUG_SPANISH should speak Spanish")
print("2. DEBUG_ENGLISH should speak English")
print("If DEBUG_SPANISH speaks English, the issue is in OpenAI TTS")
print("=" * 60)