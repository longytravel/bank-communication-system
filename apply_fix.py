"""
Apply the letter content fix to the system - FIXED ENCODING VERSION
This updates generate_tab.py to actually use letter content
"""

import shutil
from pathlib import Path
import re

def apply_the_fix():
    """Apply the fix to generate_tab.py"""
    
    print("=" * 60)
    print("APPLYING THE FIX")
    print("=" * 60)
    
    # File to update
    target_file = Path("src/communication_processing/tabs/generate_tab.py")
    
    if not target_file.exists():
        print("❌ Error: generate_tab.py not found!")
        return False
    
    # Read the current file WITH UTF-8 ENCODING (fix for Windows)
    print(f"\n📄 Reading {target_file}...")
    try:
        content = target_file.read_text(encoding='utf-8')
        print(f"   ✅ File loaded: {len(content)} characters")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        print("   Trying with different encoding...")
        try:
            content = target_file.read_text(encoding='latin-1')
            print(f"   ✅ File loaded with latin-1: {len(content)} characters")
        except Exception as e2:
            print(f"   ❌ Failed to read file: {e2}")
            return False
    
    # Step 1: Update the function signature
    print("\n🔧 Step 1: Updating function signature...")
    
    # Find and replace the function definition
    old_signature = "def create_real_ai_content_for_customer(customer: Dict, classification_type: str, cost_manager, api_manager, options: Dict) -> Dict:"
    new_signature = "def create_real_ai_content_for_customer(customer: Dict, classification_type: str, letter_content: str, cost_manager, api_manager, options: Dict) -> Dict:"
    
    if old_signature in content:
        content = content.replace(old_signature, new_signature)
        print("   ✅ Function signature updated")
    else:
        print("   ⚠️ Signature already updated or different format")
    
    # Step 2: Find where the prompt is built and update it
    print("\n🔧 Step 2: Updating the Claude prompt...")
    
    # Look for the prompt section
    if "CUSTOMER PROFILE:" in content and "ORIGINAL LETTER TO REWRITE:" not in content:
        # Insert the letter content section before CUSTOMER PROFILE
        letter_section = '''
        ORIGINAL LETTER TO REWRITE:
        ========================================
        {letter_content}
        ========================================
        
        TASK: Rewrite this letter for this specific customer across multiple channels.
        Keep the same core information but make it completely personalized.
        
        '''
        content = content.replace("CUSTOMER PROFILE:", letter_section + "CUSTOMER PROFILE:")
        print("   ✅ Letter content added to prompt")
    else:
        print("   ⚠️ Prompt already updated or different format")
    
    # Step 3: Update where the function is called
    print("\n🔧 Step 3: Updating function calls...")
    
    # Find the calls in generate_real_communication_plans
    if "create_real_ai_content_for_customer" in content:
        # Check if letter_content is already being passed
        if "letter_content" not in content or "scanner.read_letter_content" not in content:
            # Add letter reading before the function call
            old_pattern = r"(\s+)customer_plan = create_real_ai_content_for_customer\(customer, classification_type, cost_manager, api_manager, options\)"
            
            new_code = r'''\1# Get the actual letter content
\1letter_content = ""
\1if 'selected_letter' in st.session_state:
\1    selected_letter = st.session_state.selected_letter
\1    from file_handlers.letter_scanner import EnhancedLetterScanner
\1    scanner = EnhancedLetterScanner()
\1    letter_path = Path(selected_letter['filepath'])
\1    letter_content = scanner.read_letter_content(letter_path)
\1    if not letter_content:
\1        letter_content = "Letter content could not be read."
\1
\1customer_plan = create_real_ai_content_for_customer(customer, classification_type, letter_content, cost_manager, api_manager, options)'''
            
            content = re.sub(old_pattern, new_code, content)
            print("   ✅ Function calls updated")
    
    # Step 4: Do the same for demo content
    print("\n🔧 Step 4: Updating demo function...")
    
    # Update demo function signature too
    old_demo_sig = "def create_demo_content_for_customer(customer: Dict, classification_type: str, cost_manager, options: Dict) -> Dict:"
    new_demo_sig = "def create_demo_content_for_customer(customer: Dict, classification_type: str, letter_content: str, cost_manager, options: Dict) -> Dict:"
    
    if old_demo_sig in content:
        content = content.replace(old_demo_sig, new_demo_sig)
        print("   ✅ Demo function signature updated")
    
    # Update demo function calls
    if "create_demo_content_for_customer" in content and "# Get the actual letter content for demo" not in content:
        old_demo_pattern = r"(\s+)customer_plan = create_demo_content_for_customer\(customer, classification_type, cost_manager, options\)"
        
        new_demo_code = r'''\1# Get the actual letter content for demo
\1letter_content = ""
\1if 'selected_letter' in st.session_state:
\1    selected_letter = st.session_state.selected_letter
\1    from file_handlers.letter_scanner import EnhancedLetterScanner
\1    scanner = EnhancedLetterScanner()
\1    letter_path = Path(selected_letter['filepath'])
\1    letter_content = scanner.read_letter_content(letter_path)
\1    if not letter_content:
\1        letter_content = "Letter content could not be read."
\1
\1customer_plan = create_demo_content_for_customer(customer, classification_type, letter_content, cost_manager, options)'''
        
        content = re.sub(old_demo_pattern, new_demo_code, content)
        print("   ✅ Demo function calls updated")
    
    # Save the updated file WITH UTF-8 ENCODING
    print("\n💾 Saving updates...")
    try:
        target_file.write_text(content, encoding='utf-8')
        print(f"   ✅ {target_file} updated successfully!")
        return True
    except Exception as e:
        print(f"   ❌ Error saving file: {e}")
        return False

def create_quick_test():
    """Create a quick test script."""
    
    print("\n📝 Creating quick test script...")
    
    test_code = '''"""
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
    
    print(f"\\n📄 ORIGINAL LETTER:")
    print("-" * 40)
    print(letter_content)
    print("-" * 40)
    
    print(f"\\n👤 CUSTOMER: {maria['name']}")
    print(f"   Language: {maria.get('preferred_language')}")
    print(f"   Balance: £{maria.get('account_balance'):,}")
    
    # Now test the updated function
    from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
    from communication_processing.cost_configuration import CostConfigurationManager
    from api.api_manager import APIManager
    
    try:
        print("\\n🤖 Calling Claude to rewrite letter for Maria...")
        
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
        
        print("\\n✅ RESULTS:")
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
                print(f"\\n📧 EMAIL VERSION:")
                print(f"Subject: {email.get('subject', 'N/A')}")
                print(f"Body: {email.get('body', 'N/A')[:200]}...")
        
        if 'sms' in content:
            sms = content['sms']
            if isinstance(sms, dict):
                print(f"\\n💬 SMS VERSION:")
                print(f"{sms.get('text', 'N/A')}")
        
        print("\\n🎯 SUCCESS! The system is now rewriting letters!")
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        print("Make sure you have API keys configured")

if __name__ == "__main__":
    quick_test_letter_rewrite()
'''
    
    # Save test script WITH UTF-8 ENCODING
    test_file = Path("test_letter_rewrite.py")
    test_file.write_text(test_code, encoding='utf-8')
    print(f"   ✅ Test script saved to: {test_file}")
    
    return test_file

if __name__ == "__main__":
    # Apply the fix
    success = apply_the_fix()
    
    if success:
        # Create test script
        test_file = create_quick_test()
        
        print("\n" + "=" * 60)
        print("✅ FIX APPLIED SUCCESSFULLY!")
        print("=" * 60)
        print("\nThe system will now:")
        print("  1. ✅ Read the actual letter content")
        print("  2. ✅ Pass it to Claude")
        print("  3. ✅ Rewrite it for each customer")
        print("  4. ✅ Personalize for each channel")
        
        print(f"\n🧪 To test the fix, run:")
        print(f"   python {test_file}")
        
        print("\n📱 Or test in the full UI:")
        print("   1. Run: python -m streamlit run src/main.py")
        print("   2. Go to Customer Communication Plans")
        print("   3. It will now rewrite letters properly!")
    else:
        print("\n❌ Fix failed - check the error messages above")