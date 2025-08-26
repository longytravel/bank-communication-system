"""
Quick test to verify letter content is being used
Run this AFTER applying the fix
"""

import sys
from pathlib import Path
sys.path.append('src')

from create_test_dataset import load_test_dataset

def quick_test_letter_rewrite():
    """Quick test with Maria to see if letter is rewritten."""
    
    print("=" * 60)
    print("TESTING LETTER REWRITE WITH MARIA")
    print("=" * 60)
    
    # Load test data
    test_data = load_test_dataset()
    maria = test_data['customer_categories'][0]
    
    # Sample letter content
    letter_content = """
    Dear Customer,
    
    We are writing to inform you about important changes to your account.
    Your current balance and transaction limits have been reviewed.
    Please log into your online banking to review these changes.
    
    Thank you for being a valued customer.
    
    Sincerely,
    Resonance Bank
    """
    
    print(f"\n📄 ORIGINAL LETTER:")
    print("-" * 40)
    print(letter_content)
    print("-" * 40)
    
    print(f"\n👤 CUSTOMER: {maria['name']}")
    print(f"   Language: {maria.get('preferred_language')}")
    print(f"   Balance: £{maria.get('account_balance'):,}")
    
    # Now test the updated function
    from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
    from communication_processing.cost_configuration import CostConfigurationManager
    from api.api_manager import APIManager
    
    try:
        print("\n🤖 Calling Claude to rewrite letter for Maria...")
        
        cost_manager = CostConfigurationManager()
        api_manager = APIManager()
        options = {'generate_videos': False}
        
        result = create_real_ai_content_for_customer(
            maria,
            "INFORMATION",
            letter_content,  # NOW WE PASS THE LETTER!
            cost_manager,
            api_manager,
            options
        )
        
        print("\n✅ RESULTS:")
        print("-" * 40)
        
        # Check if it was rewritten
        if result.get('letter_rewritten'):
            print("✅ Letter was rewritten!")
        else:
            print("❌ Letter was NOT rewritten (used template)")
        
        # Show the personalized content
        content = result.get('content', {})
        
        if 'email' in content:
            email = content['email']
            if isinstance(email, dict):
                print(f"\n📧 EMAIL VERSION:")
                print(f"Subject: {email.get('subject', 'N/A')}")
                print(f"Body: {email.get('body', 'N/A')[:200]}...")
        
        if 'sms' in content:
            sms = content['sms']
            if isinstance(sms, dict):
                print(f"\n💬 SMS VERSION:")
                print(f"{sms.get('text', 'N/A')}")
        
        print("\n🎯 SUCCESS! The system is now rewriting letters!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you have API keys configured")

if __name__ == "__main__":
    quick_test_letter_rewrite()
