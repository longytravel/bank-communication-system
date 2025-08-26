"""
Complete fix for deep personalization - forces Claude to use ALL customer data points
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

def apply_complete_personalization_fix():
    """Apply the complete fix for deep personalization."""
    
    print("=" * 60)
    print("APPLYING COMPLETE PERSONALIZATION FIX")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Find the create_real_ai_content_for_customer function
    # Replace the prompt section with a much more aggressive version
    
    new_prompt_section = '''
        # CRITICAL: Build very specific personalization requirements
        personalization_requirements = f"""
        YOU MUST USE THESE EXACT DATA POINTS IN YOUR RESPONSE:
        
        MANDATORY REFERENCES (USE THE EXACT NUMBERS):
        ✓ Balance: You MUST mention "£{customer.get('account_balance', 0):,}" explicitly
        ✓ Age: You MUST reference "{customer.get('age', 'Unknown')} years" when relevant
        ✓ Usage: You MUST mention "{customer.get('digital_logins_per_month', 0)} logins per month"
        ✓ Products: You MUST list these specific products: {', '.join(upsell_products) if upsell_products else 'standard services'}
        
        EXAMPLE OF WHAT YOU MUST DO:
        ❌ WRONG: "As a valued customer..." 
        ✅ RIGHT: "With your £{customer.get('account_balance', 0):,} balance..."
        
        ❌ WRONG: "You're eligible for premium services"
        ✅ RIGHT: "You qualify for: {', '.join(upsell_products)}"
        
        ❌ WRONG: "As an active user..."
        ✅ RIGHT: "Your {customer.get('digital_logins_per_month', 0)} monthly logins show..."
        """
        
        # Create comprehensive prompt for all channels
        prompt = f"""
        {language_instruction}
        
        {personalization_requirements}
        
        ORIGINAL LETTER TO REWRITE:
        ========================================
        {letter_content}
        ========================================
        
        CUSTOMER DATA TO USE IN PERSONALIZATION:
        - Name: {name}
        - Balance: £{customer.get('account_balance', 0):,} (USE THIS NUMBER)
        - Age: {customer.get('age', 'Unknown')} years old (USE THIS NUMBER)
        - Monthly logins: {customer.get('digital_logins_per_month', 0)} times (USE THIS NUMBER)
        - Eligible products: {', '.join(upsell_products) if upsell_products else 'None'} (LIST THESE)
        - Email: {customer.get('email', 'Not provided')}
        - Account health: {account_health}
        - Category: {category}
        - Language: {customer_language}
        
        TASK: Rewrite the letter using ALL the specific data points above.
        
        For EACH channel, you MUST:
        1. Include the customer's EXACT balance (£{customer.get('account_balance', 0):,})
        2. Reference their SPECIFIC usage ({customer.get('digital_logins_per_month', 0)} logins/month)
        3. Mention their age if relevant ({customer.get('age', 'Unknown')} years)
        4. List their specific eligible products by name
        
        Generate content for these channels: {', '.join(channels)}
    '''
    
    # Find and replace the prompt building section
    import re
    
    # Pattern to find the prompt creation
    pattern = r'prompt = f"""[\s\S]*?"""'
    
    # Check if we can find it
    if 'prompt = f"""' in content:
        # Replace the entire prompt section
        content = re.sub(pattern, new_prompt_section, content, count=1)
        print("✅ Prompt section replaced with enhanced version")
    else:
        print("⚠️ Could not find prompt section to replace")
    
    # Also update the system message to be more strict
    old_system = r'system_message = f"""[^"]*"""'
    new_system = '''system_message = f"""You are a banking specialist who MUST use SPECIFIC NUMBERS from customer data.
        
        CRITICAL RULES:
        1. ALWAYS use the EXACT balance amount (e.g., "£50,000" not "high balance")
        2. ALWAYS use the EXACT login count (e.g., "45 logins" not "frequent user")  
        3. ALWAYS use the EXACT age when relevant (e.g., "at 32 years old")
        4. ALWAYS list the SPECIFIC product names (e.g., "Wealth Management, Premium Credit Card")
        5. NEVER use generic terms like "valued customer" or "premium tier"
        
        Generate all content in {customer_language}."""'''
    
    content = re.sub(old_system, new_system, content, flags=re.DOTALL)
    print("✅ System message updated for strict data usage")
    
    # Save the updated file
    file_path.write_text(content, encoding='utf-8')
    print("✅ File updated successfully")
    
    return True

def create_comprehensive_test():
    """Create a comprehensive test for the fix."""
    
    test_code = '''"""
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
        print(f"\\n{'='*40}")
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
        
        print(f"\\n📊 Data Point Usage:")
        score = 0
        for item, found in checks.items():
            status = "✅" if found else "❌"
            print(f"  {status} {item}")
            if found:
                score += 1
        
        total = len(checks)
        percentage = (score/total*100) if total > 0 else 0
        print(f"\\n📈 Score: {score}/{total} ({percentage:.0f}%)")
        all_scores.append(percentage)
    
    # Overall summary
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    print(f"\\n{'='*60}")
    print(f"OVERALL PERSONALIZATION SCORE: {avg_score:.0f}%")
    
    if avg_score >= 80:
        print("🎉 EXCELLENT! Deep personalization is working well!")
    elif avg_score >= 60:
        print("✅ Good progress, but room for improvement")
    else:
        print("⚠️ Needs more work on personalization")

if __name__ == "__main__":
    test_complete_personalization()
'''
    
    test_file = Path("test_complete_personalization.py")
    test_file.write_text(test_code, encoding='utf-8')
    print(f"\n📝 Test script created: {test_file}")
    return test_file

if __name__ == "__main__":
    # Backup first
    backup_dir = backup_file()
    
    # Apply the fix
    if apply_complete_personalization_fix():
        test_file = create_comprehensive_test()
        
        print("\n" + "=" * 60)
        print("✅ COMPLETE PERSONALIZATION FIX APPLIED!")
        print("=" * 60)
        print("\nThe system will now:")
        print("  1. ✅ FORCE use of exact balance amounts")
        print("  2. ✅ FORCE use of specific login counts")
        print("  3. ✅ FORCE use of customer age")
        print("  4. ✅ FORCE listing of specific products")
        print("  5. ✅ Track success with comprehensive testing")
        
        print(f"\n🧪 Run the comprehensive test:")
        print(f"   python {test_file}")
        
        print(f"\n🛡️ Backup saved: {backup_dir}")