"""
Test that letters are ACTUALLY rewritten with same content
"""

import sys
from pathlib import Path
sys.path.append('src')

from create_test_dataset import load_test_dataset
from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
from communication_processing.cost_configuration import CostConfigurationManager
from api.api_manager import APIManager

def test_strict_rewrite():
    """Test that content is preserved."""
    
    print("=" * 60)
    print("TESTING STRICT LETTER REWRITE")
    print("=" * 60)
    
    # Letter with SPECIFIC features
    test_letter = """
    Money Management Tools Available
    
    We offer three helpful features:
    1. Spending Limits - Set your own caps
    2. Real-time Alerts - Get instant notifications  
    3. Savings Tracker - Monitor your goals
    
    Visit example.com/tools or call 0800-123-456
    """
    
    print("ORIGINAL LETTER:")
    print(test_letter)
    print("-" * 40)
    
    # Test with Vera (vulnerable)
    test_data = load_test_dataset()
    vera = test_data['customer_categories'][1]  # Vulnerable Vera
    
    print(f"\nTesting with: {vera['name']} ({vera['category']})")
    
    cost_manager = CostConfigurationManager()
    api_manager = APIManager()
    
    result = create_real_ai_content_for_customer(
        vera,
        "INFORMATION",
        test_letter,
        cost_manager,
        api_manager,
        {'generate_videos': False}
    )
    
    # Check the content
    content = result.get('content', {})
    
    print("\n✅ CHECKING REWRITTEN CONTENT:")
    print("-" * 40)
    
    checks = {
        "Spending Limits": False,
        "Alerts": False,
        "Savings": False,
        "0800-123-456": False
    }
    
    # Check email
    if 'email' in content:
        email_body = str(content['email'].get('body', ''))
        print(f"\nEMAIL: {email_body[:200]}...")
        
        for key in checks:
            if key.lower() in email_body.lower():
                checks[key] = True
    
    print(f"\n📊 CONTENT PRESERVATION CHECK:")
    for item, found in checks.items():
        status = "✅" if found else "❌"
        print(f"  {status} {item}: {'FOUND' if found else 'MISSING'}")
    
    if all(checks.values()):
        print("\n🎉 SUCCESS! Letter content preserved!")
    else:
        print("\n⚠️ Some content still missing")

if __name__ == "__main__":
    test_strict_rewrite()
