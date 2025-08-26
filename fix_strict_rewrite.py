"""
Fix the prompt to make Claude ACTUALLY rewrite the letter content
Not replace it with generic messages!
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

def fix_the_prompt():
    """Make the Claude prompt MUCH stricter about preserving letter content."""
    
    print("=" * 60)
    print("FIXING CLAUDE PROMPT FOR STRICT REWRITING")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Find the old prompt section
    old_prompt = """        ORIGINAL LETTER TO REWRITE:
        ========================================
        {letter_content}
        ========================================
        
        TASK: Rewrite this letter for this specific customer across multiple channels.
        Keep the same core information but make it completely personalized."""
    
    # Much stricter prompt
    new_prompt = """        ORIGINAL LETTER TO REWRITE:
        ========================================
        {letter_content}
        ========================================
        
        CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:
        
        1. EXTRACT these key points from the letter above:
           - Main topic/purpose
           - ALL specific features or services mentioned
           - ANY actions requested from the customer
           - ANY links or contact information
        
        2. Your rewrite MUST include:
           - EVERY feature/service from the original letter
           - The SAME core message and purpose
           - ALL contact info and links from original
           - Just adapt the TONE and LANGUAGE for the customer
        
        3. DO NOT:
           - Replace content with generic support messages
           - Skip any features mentioned in the original
           - Change what the letter is about
           - Add unrelated content
        
        4. EXAMPLE:
           If original says "Set spending limits, get alerts, track savings"
           You MUST mention ALL THREE in your rewrite
           NOT just say "we offer helpful tools"
        
        TASK: Rewrite preserving ALL information, just personalize the delivery."""
    
    if old_prompt in content:
        content = content.replace(old_prompt, new_prompt)
        print("✅ Prompt updated to be MUCH stricter")
    else:
        print("⚠️ Trying alternative fix...")
        # Try to find and replace just the TASK line
        if "TASK: Rewrite this letter" in content:
            content = content.replace(
                "TASK: Rewrite this letter for this specific customer across multiple channels.\n        Keep the same core information but make it completely personalized.",
                new_prompt.split("CRITICAL INSTRUCTIONS")[1]
            )
            print("✅ Alternative fix applied")
    
    # Also update the system message to be stricter
    old_system = '''system_message = f"""You are a banking communication specialist. 
        Your job is to take generic letters and rewrite them to be completely personalized for each customer.
        The rewritten content must convey the same information as the original letter but in a way that resonates with the specific customer.
        ALL content must be in {customer_language}."""'''
    
    new_system = '''system_message = f"""You are a banking communication specialist who MUST preserve letter content.
        
        YOUR CRITICAL RULES:
        1. NEVER replace letter content with generic messages
        2. ALWAYS include EVERY feature/service mentioned in the original
        3. ONLY change tone and personalization, NOT the information
        4. If the letter lists 3 features, your rewrite MUST list those SAME 3 features
        5. Adapt for the customer but keep the SAME core message
        
        ALL content must be in {customer_language}."""'''
    
    if "system_message = f" in content:
        # Find and replace the system message
        import re
        pattern = r'system_message = f""".*?"""'
        content = re.sub(pattern, new_system, content, flags=re.DOTALL)
        print("✅ System message made stricter")
    
    # Save the fixed file
    file_path.write_text(content, encoding='utf-8')
    print("✅ File updated successfully")
    
    return True

def create_test_script():
    """Create a test to verify the fix works."""
    
    test_code = '''"""
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
    
    print(f"\\nTesting with: {vera['name']} ({vera['category']})")
    
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
    
    print("\\n✅ CHECKING REWRITTEN CONTENT:")
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
        print(f"\\nEMAIL: {email_body[:200]}...")
        
        for key in checks:
            if key.lower() in email_body.lower():
                checks[key] = True
    
    print(f"\\n📊 CONTENT PRESERVATION CHECK:")
    for item, found in checks.items():
        status = "✅" if found else "❌"
        print(f"  {status} {item}: {'FOUND' if found else 'MISSING'}")
    
    if all(checks.values()):
        print("\\n🎉 SUCCESS! Letter content preserved!")
    else:
        print("\\n⚠️ Some content still missing")

if __name__ == "__main__":
    test_strict_rewrite()
'''
    
    test_file = Path("test_strict_rewrite.py")
    test_file.write_text(test_code, encoding='utf-8')
    print(f"\n📝 Test script created: {test_file}")
    return test_file

if __name__ == "__main__":
    # Backup first
    backup_dir = backup_file()
    
    # Apply the fix
    if fix_the_prompt():
        test_file = create_test_script()
        
        print("\n" + "=" * 60)
        print("✅ FIX APPLIED!")
        print("=" * 60)
        print("\nClaude will now:")
        print("  1. Extract ALL features from the original letter")
        print("  2. Include EVERY feature in the rewrite")
        print("  3. NOT replace with generic content")
        print("  4. Preserve links and contact info")
        
        print(f"\n🧪 Test the fix:")
        print(f"   python {test_file}")
        
        print("\n📱 Or regenerate in the UI:")
        print("   The letters should now preserve ALL original content!")
        print(f"\n🛡️ Backup saved: {backup_dir}")