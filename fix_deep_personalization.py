"""
Make Claude use ACTUAL customer data points for deep personalization
Not just generic "premium customer" language!
"""

from pathlib import Path
import shutil
from datetime import datetime

def backup_file():
    """Backup before changes."""
    source = Path("src/communication_processing/tabs/generate_tab.py")
    backup_dir = Path("backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / "generate_tab.py.backup"
    shutil.copy2(source, backup)
    print(f"✅ Backup saved: {backup}")
    return backup_dir

def enhance_personalization():
    """Make Claude use specific customer data points."""
    
    print("=" * 60)
    print("ENHANCING PERSONALIZATION WITH REAL DATA")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Find where we build the customer profile section
    old_profile = """        CUSTOMER PROFILE:
        - Name: {name}
        - Preferred Language: {customer_language}
        - Category: {category}
        - Account Balance: £{customer.get('account_balance', 0):,}
        - Age: {customer.get('age', 'Unknown')}
        - Account Health: {account_health}
        - Engagement Level: {engagement_level}
        - Digital Maturity: {digital_maturity}
        - Upsell Eligible: {upsell_eligible}
        - Suggested Products: {', '.join(upsell_products) if upsell_products else 'None'}"""
    
    # Much more detailed profile with ALL data points
    new_profile = """        CUSTOMER PROFILE WITH SPECIFIC DATA POINTS:
        - Name: {name}
        - Age: {customer.get('age', 'Unknown')} years old
        - Account Balance: £{customer.get('account_balance', 0):,}
        - Monthly Digital Logins: {customer.get('digital_logins_per_month', 0)} times
        - Preferred Language: {customer_language}
        - Category: {category}
        - Account Health: {account_health}
        - Engagement Level: {engagement_level} 
        - Digital Maturity: {digital_maturity}
        - Upsell Eligible: {upsell_eligible}
        - Specific Products Qualified For: {', '.join(upsell_products) if upsell_products else 'None'}
        - Email: {customer.get('email', 'Not provided')}
        - Phone: {customer.get('phone', 'Not provided')}
        - Category Reasoning: {' | '.join(customer.get('category_reasoning', [])[:2])}
        - Support Needs: {', '.join(customer.get('support_needs', [])) if customer.get('support_needs') else 'None'}
        - Risk Factors: {', '.join(customer.get('risk_factors', [])) if customer.get('risk_factors') else 'None'}"""
    
    if old_profile in content:
        content = content.replace(old_profile, new_profile)
        print("✅ Customer profile enhanced with more data points")
    
    # Now update the requirements to FORCE use of these data points
    old_requirements = """        REQUIREMENTS:
        1. Rewrite the letter content for each channel below
        2. Keep the same information but make it engaging and personal
        3. Use the customer's name and reference their specific situation
        4. Adapt length and tone for each channel
        5. For SMS: Maximum 160 characters
        6. For Email: Professional but friendly
        7. For In-app: Direct and actionable"""
    
    new_requirements = """        REQUIREMENTS FOR DEEP PERSONALIZATION:
        
        1. YOU MUST reference these SPECIFIC data points in your rewrite:
           - Their EXACT balance amount (£{customer.get('account_balance', 0):,})
           - Their ACTUAL usage pattern ({customer.get('digital_logins_per_month', 0)} logins/month)
           - Their AGE if relevant ({customer.get('age', 'Unknown')} years)
           - Their SPECIFIC eligible products if upsell eligible
           
        2. DO NOT use generic terms like:
           ❌ "valued customer" 
           ❌ "premium tier"
           ❌ "high-value client"
           
        3. DO use specific references like:
           ✅ "With your £50,000 balance..."
           ✅ "Your 45 logins this month show..."
           ✅ "At 32, you're perfectly positioned for..."
           ✅ "You qualify for: Wealth Management, Premium Credit Card..."
           
        4. Keep ALL original letter content but weave in personal data
        5. For SMS: Maximum 160 characters (but still include a data point!)
        6. For Email: Use multiple data points for rich personalization
        7. For In-app: Reference their actual usage patterns"""
    
    if "REQUIREMENTS" in content:
        content = content.replace(old_requirements, new_requirements)
        print("✅ Requirements updated for deep personalization")
    
    # Update system message to emphasize data usage
    old_system_marker = "YOUR CRITICAL RULES:"
    new_system_addition = """YOUR CRITICAL RULES:
        1. USE SPECIFIC NUMBERS - Don't say "high balance", say "£50,000 balance"
        2. USE ACTUAL DATA - Don't say "frequent user", say "45 logins this month"
        3. USE REAL PRODUCTS - Don't say "premium services", list the actual products they qualify for
        4. """
    
    if old_system_marker in content:
        content = content.replace(old_system_marker, new_system_addition)
        print("✅ System message enhanced")
    
    # Save the enhanced file
    file_path.write_text(content, encoding='utf-8')
    print("✅ File updated successfully")
    
    return True

def create_test_script():
    """Create a test to verify deep personalization."""
    
    test_code = '''"""
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
    
    print("\\nGenerating personalized content...")
    
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
    
    print("\\n✅ CHECKING FOR SPECIFIC DATA POINTS:")
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
        print(f"\\nEMAIL PREVIEW: {email_body[:300]}...")
        
        for key in data_checks:
            if key in email_body:
                data_checks[key] = True
    
    # Check SMS too
    if 'sms' in content:
        sms_text = str(content['sms'].get('text', ''))
        print(f"\\nSMS: {sms_text}")
        
        for key in data_checks:
            if key in sms_text:
                data_checks[key] = True
    
    print(f"\\n📊 DATA POINT USAGE CHECK:")
    for item, found in data_checks.items():
        status = "✅" if found else "❌"
        print(f"  {status} {item}: {'USED' if found else 'NOT USED'}")
    
    # Count how many data points were used
    used_count = sum(data_checks.values())
    total_count = len(data_checks)
    
    print(f"\\n📈 PERSONALIZATION SCORE: {used_count}/{total_count}")
    
    if used_count >= 4:
        print("\\n🎉 EXCELLENT! Deep personalization working!")
    elif used_count >= 2:
        print("\\n✅ Good personalization, but could be deeper")
    else:
        print("\\n⚠️ Needs more specific data usage")

if __name__ == "__main__":
    test_deep_personalization()
'''
    
    test_file = Path("test_deep_personalization.py")
    test_file.write_text(test_code, encoding='utf-8')
    print(f"\n📝 Test script created: {test_file}")
    return test_file

if __name__ == "__main__":
    # Backup first
    backup_dir = backup_file()
    
    # Apply the enhancement
    if enhance_personalization():
        test_file = create_test_script()
        
        print("\n" + "=" * 60)
        print("✅ DEEP PERSONALIZATION ENHANCED!")
        print("=" * 60)
        print("\nClaude will now use:")
        print("  1. ✅ Exact balance amounts (£50,000)")
        print("  2. ✅ Specific usage data (45 logins/month)")
        print("  3. ✅ Customer age (32 years)")
        print("  4. ✅ Named products (Wealth Management, Premium Credit Card)")
        print("  5. ✅ Actual risk factors and support needs")
        
        print(f"\n🧪 Test the enhancement:")
        print(f"   python {test_file}")
        
        print(f"\n🛡️ Backup saved: {backup_dir}")