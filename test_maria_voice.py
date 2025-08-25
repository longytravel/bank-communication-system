"""
Test Maria's voice note generation with Spanish content
"""

import sys
sys.path.append('src')

from api.api_manager import APIManager

print("=" * 60)
print("TESTING MARIA'S VOICE NOTE GENERATION")
print("=" * 60)

# Maria's data with Spanish preference
maria_data = {
    'customer_id': 'CUST011',
    'name': 'Maria Garcia',
    'preferred_language': 'Spanish',
    'category': 'Digital-first self-serve',
    'account_balance': 25000
}

# Test texts
english_text = "Hello Maria, your account balance is healthy and you have been pre-approved for our premium card."
spanish_text = "Hola Maria, el saldo de su cuenta está saludable y ha sido preaprobada para nuestra tarjeta premium."

try:
    # Initialize API manager
    api_manager = APIManager()
    
    print("\n1. Testing with ENGLISH text (should detect Spanish from customer data):")
    print(f"   Text: {english_text[:50]}...")
    
    # Test 1: English text but Spanish customer
    result1 = api_manager.openai.generate_voice_note(
        english_text,
        "MARIA_TEST_1",
        "notification",
        customer_language="Spanish"  # Explicitly pass Spanish
    )
    
    if result1:
        print(f"   ✅ Voice note created: {result1.name}")
    else:
        print("   ❌ Failed to create voice note")
    
    print("\n2. Testing with SPANISH text:")
    print(f"   Text: {spanish_text[:50]}...")
    
    # Test 2: Spanish text
    result2 = api_manager.openai.generate_voice_note(
        spanish_text,
        "MARIA_TEST_2",
        "notification",
        customer_language="Spanish"
    )
    
    if result2:
        print(f"   ✅ Voice note created: {result2.name}")
    else:
        print("   ❌ Failed to create voice note")
    
    print("\n3. Testing the FULL communication flow:")
    
    # This simulates what happens in the real system
    test_strategy = {
        "assets": {
            "voice_note_text": spanish_text  # This should be Spanish
        }
    }
    
    # Test the method that actually generates voice for a customer
    result3 = api_manager._generate_voice_note_for_customer(
        test_strategy,
        "MARIA_TEST_3",
        maria_data
    )
    
    if result3:
        print(f"   ✅ Full flow voice note created: {result3.name}")
    else:
        print("   ❌ Full flow failed")
        
    print("\n4. Checking what text Maria actually gets:")
    
    # Simulate the real communication processing
    letter_text = "Important account update"
    
    strategy = api_manager.claude.process_customer_letter(
        letter_text,
        maria_data,
        ["in_app", "email", "sms", "voice_note"]
    )
    
    if strategy and "assets" in strategy:
        assets = strategy["assets"]
        print(f"   Voice note text from Claude: {assets.get('voice_note_text', 'NOT FOUND')[:100]}...")
        print(f"   SMS text from Claude: {assets.get('sms_text', 'NOT FOUND')[:100]}...")
        print(f"   In-app text from Claude: {assets.get('in_app_notification', 'NOT FOUND')[:100]}...")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Check the generated MP3 files to hear if they're in Spanish")
print("=" * 60)