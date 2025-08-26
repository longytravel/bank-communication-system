"""
Comprehensive test for complete personalization
"""

import sys
from pathlib import Path
sys.path.append('src')

from create_test_dataset import load_test_dataset
from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
from communication_processing.cost_configuration import CostConfigurationManager
from api.api_manager import APIManager

def test_complete_personalization():
    """Test that ALL data points are used."""
    
    print("=" * 60)
    print("TESTING COMPLETE PERSONALIZATION")
    print("=" * 60)
    
    # Letter to personalize
    test_letter = """
    Important Account Update
    
    We're writing to inform you about new features available for your account.
    These include spending controls, alerts, and savings tools.
    
    Please review these options at your convenience.
    """
    
    # Test with all three customers
    test_data = load_test_dataset()
    
    cost_manager = CostConfigurationManager()
    api_manager = APIManager()
    
    all_scores = []
    
    for i, customer in enumerate(test_data['customer_categories']):
        print(f"\n{'='*40}")
        print(f"Testing Customer {i+1}: {customer['name']}")
        print(f"  Balance: £{customer['account_balance']:,}")
        print(f"  Age: {customer['age']}")
        print(f"  Logins: {customer['digital_logins_per_month']}/month")
        print(f"  Products: {', '.join(customer.get('upsell_products', []))}")
        
        result = create_real_ai_content_for_customer(
            customer,
            "INFORMATION",
            test_letter,
            cost_manager,
            api_manager,
            {'generate_videos': False}
        )
        
        content = result.get('content', {})
        
        # Check all content for data points
        all_content = ""
        if 'email' in content:
            all_content += str(content['email'].get('body', ''))
        if 'sms' in content:
            all_content += str(content['sms'].get('text', ''))
        if 'in_app' in content:
            all_content += str(content['in_app'].get('message_body', ''))
        
        # Check for specific data points
        balance_str = f"£{customer['account_balance']:,}"
        age_str = str(customer['age'])
        login_str = str(customer['digital_logins_per_month'])
        
        checks = {
            f"Balance ({balance_str})": balance_str in all_content,
            f"Age ({age_str})": age_str in all_content,
            f"Logins ({login_str})": login_str in all_content,
        }
        
        # Check for products
        for product in customer.get('upsell_products', []):
            checks[f"Product: {product}"] = product in all_content
        
        print(f"\n📊 Data Point Usage:")
        score = 0
        for item, found in checks.items():
            status = "✅" if found else "❌"
            print(f"  {status} {item}")
            if found:
                score += 1
        
        total = len(checks)
        percentage = (score/total*100) if total > 0 else 0
        print(f"\n📈 Score: {score}/{total} ({percentage:.0f}%)")
        all_scores.append(percentage)
    
    # Overall summary
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    print(f"\n{'='*60}")
    print(f"OVERALL PERSONALIZATION SCORE: {avg_score:.0f}%")
    
    if avg_score >= 80:
        print("🎉 EXCELLENT! Deep personalization is working well!")
    elif avg_score >= 60:
        print("✅ Good progress, but room for improvement")
    else:
        print("⚠️ Needs more work on personalization")

if __name__ == "__main__":
    test_complete_personalization()
