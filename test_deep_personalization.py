"""
Test that REAL data points are used in personalization
"""

import sys
from pathlib import Path
sys.path.append('src')

from create_test_dataset import load_test_dataset
from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
from communication_processing.cost_configuration import CostConfigurationManager
from api.api_manager import APIManager

def test_deep_personalization():
    """Test that specific data points are used."""
    
    print("=" * 60)
    print("TESTING DEEP PERSONALIZATION")
    print("=" * 60)
    
    # Simple letter to personalize
    test_letter = """
    Money Management Tools
    We offer spending limits, alerts, and savings tracking.
    Visit our website or call us.
    """
    
    # Load Dave - he has rich data
    test_data = load_test_dataset()
    dave = test_data['customer_categories'][2]  # Digital Dave
    
    print(f"CUSTOMER DATA:")
    print(f"  Name: {dave['name']}")
    print(f"  Balance: £{dave['account_balance']:,}")
    print(f"  Logins/month: {dave['digital_logins_per_month']}")
    print(f"  Age: {dave['age']}")
    print(f"  Products: {', '.join(dave.get('upsell_products', []))}")
    print("-" * 40)
    
    cost_manager = CostConfigurationManager()
    api_manager = APIManager()
    
    print("\nGenerating personalized content...")
    
    result = create_real_ai_content_for_customer(
        dave,
        "INFORMATION",
        test_letter,
        cost_manager,
        api_manager,
        {'generate_videos': False}
    )
    
    # Check the content
    content = result.get('content', {})
    
    print("\n✅ CHECKING FOR SPECIFIC DATA POINTS:")
    print("-" * 40)
    
    # Check for specific data points
    data_checks = {
        "£50,000": False,  # Exact balance
        "45": False,       # Login count
        "32": False,       # Age
        "Wealth Management": False,  # Specific product
        "Premium Credit Card": False,
        "Investment ISA": False
    }
    
    # Check email for data points
    if 'email' in content:
        email_body = str(content['email'].get('body', ''))
        print(f"\nEMAIL PREVIEW: {email_body[:300]}...")
        
        for key in data_checks:
            if key in email_body:
                data_checks[key] = True
    
    # Check SMS too
    if 'sms' in content:
        sms_text = str(content['sms'].get('text', ''))
        print(f"\nSMS: {sms_text}")
        
        for key in data_checks:
            if key in sms_text:
                data_checks[key] = True
    
    print(f"\n📊 DATA POINT USAGE CHECK:")
    for item, found in data_checks.items():
        status = "✅" if found else "❌"
        print(f"  {status} {item}: {'USED' if found else 'NOT USED'}")
    
    # Count how many data points were used
    used_count = sum(data_checks.values())
    total_count = len(data_checks)
    
    print(f"\n📈 PERSONALIZATION SCORE: {used_count}/{total_count}")
    
    if used_count >= 4:
        print("\n🎉 EXCELLENT! Deep personalization working!")
    elif used_count >= 2:
        print("\n✅ Good personalization, but could be deeper")
    else:
        print("\n⚠️ Needs more specific data usage")

if __name__ == "__main__":
    test_deep_personalization()
