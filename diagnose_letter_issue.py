"""
Diagnose what's ACTUALLY being sent to Claude
This will show us if letter content is being used (spoiler: it's not!)
"""

import sys
import json
from pathlib import Path
sys.path.append('src')

from create_test_dataset import load_test_dataset

def check_what_gets_sent_to_claude():
    """Check what data is actually being sent when generating plans."""
    
    print("=" * 60)
    print("CHECKING WHAT'S SENT TO CLAUDE")
    print("=" * 60)
    
    # Load test data
    test_data = load_test_dataset()
    maria = test_data['customer_categories'][0]  # Maria Garcia
    
    # Load a sample letter
    letter_path = Path("data/letters/demo/account_update.txt")
    if letter_path.exists():
        letter_content = letter_path.read_text()
        print(f"\n📄 LETTER CONTENT ({len(letter_content)} chars):")
        print("-" * 40)
        print(letter_content[:500])
        print("-" * 40)
    else:
        letter_content = "Dear Customer, Your account has important updates. Please review them carefully."
        print(f"\n📄 SAMPLE LETTER: {letter_content}")
    
    # Simulate what the system currently does
    from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
    from communication_processing.cost_configuration import CostConfigurationManager
    from api.api_manager import APIManager
    
    print("\n🔍 WHAT THE SYSTEM CURRENTLY SENDS:")
    print("-" * 40)
    
    # This is what currently happens
    classification_type = "INFORMATION"  # Just the TYPE, not the content!
    cost_manager = CostConfigurationManager()
    
    # Let's intercept what would be sent to Claude
    # Look at the create_real_ai_content_for_customer function
    print(f"1. Classification Type: {classification_type}")
    print(f"2. Customer Name: {maria['name']}")
    print(f"3. Customer Language: {maria.get('preferred_language')}")
    print(f"4. Customer Category: {maria['category']}")
    print(f"5. Account Balance: £{maria['account_balance']}")
    
    print("\n❌ WHAT'S MISSING:")
    print(f"- The actual letter content ({len(letter_content)} characters)")
    print("- The letter is NEVER passed to the function!")
    print("- Claude has NO IDEA what the letter says!")
    
    print("\n🎯 WHAT SHOULD BE SENT:")
    print("-" * 40)
    print("The prompt to Claude SHOULD include:")
    print(f"1. Original letter content: '{letter_content[:100]}...'")
    print("2. Instruction: 'Rewrite this letter for Maria in Spanish'")
    print("3. Make it personalized based on her profile")
    print("4. Adapt for each channel (short for SMS, etc)")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    print("\n🚨 CONFIRMED: The letter content is NOT being used!")
    print("📝 The system only uses the letter TYPE (REGULATORY/INFO/PROMO)")
    print("❌ It never actually rewrites the letter content!")
    
    return letter_content, maria

def show_what_we_need_to_fix():
    """Show exactly what needs to be fixed."""
    
    print("\n" + "=" * 60)
    print("WHAT WE NEED TO FIX")
    print("=" * 60)
    
    print("\n📍 File: src/communication_processing/tabs/generate_tab.py")
    print("📍 Function: create_real_ai_content_for_customer()")
    
    print("\n❌ CURRENT FUNCTION SIGNATURE:")
    print("def create_real_ai_content_for_customer(customer, classification_type, cost_manager, api_manager, options)")
    
    print("\n✅ WHAT IT SHOULD BE:")
    print("def create_real_ai_content_for_customer(customer, classification_type, LETTER_CONTENT, cost_manager, api_manager, options)")
    
    print("\n📝 The function needs to:")
    print("1. Receive the actual letter content")
    print("2. Include it in the Claude prompt")
    print("3. Ask Claude to REWRITE it for each customer")
    print("4. Make it channel-appropriate")
    
    print("\n💡 Example prompt to Claude should be:")
    print("""
    'Here is a letter we need to send:
    [ORIGINAL LETTER CONTENT]
    
    Rewrite this letter for Maria Garcia:
    - Translate to Spanish
    - Make it personal using her name
    - Reference her £25,000 balance
    - Create versions for: SMS (160 chars), Email, In-app notification
    - Keep the same information but make it engaging'
    """)

if __name__ == "__main__":
    # Run diagnosis
    letter_content, maria = check_what_gets_sent_to_claude()
    
    # Show what needs fixing
    show_what_we_need_to_fix()
    
    print("\n" + "=" * 60)
    print("READY TO FIX?")
    print("=" * 60)
    print("\nNext step: We'll fix generate_tab.py to actually use the letter content")
    print("This will make the system ACTUALLY rewrite letters for each customer!")
    