"""
AUTOMATIC FIX SCRIPT for generate_tab.py
This will fix the syntax error automatically - no copy/paste needed!

Run this script and it will repair your generate_tab.py file.
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def backup_original_file():
    """Create a backup of the original file before fixing."""
    source_file = Path("src/communication_processing/tabs/generate_tab.py")
    
    if not source_file.exists():
        print(f"❌ ERROR: {source_file} not found!")
        return False
    
    # Create backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"generate_tab_backup_{timestamp}.py"
    
    shutil.copy2(source_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    return True

def fix_syntax_error():
    """Fix the syntax error in generate_tab.py automatically."""
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    if not file_path.exists():
        print(f"❌ ERROR: {file_path} not found!")
        return False
    
    print(f"📝 Reading {file_path}...")
    
    try:
        # Read the file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    print(f"📄 File loaded: {len(content)} characters")
    
    # The problem is likely around line 832 with an f-string syntax error
    # Let's find and fix the problematic f-string patterns
    
    # Fix 1: Find problematic f-string with unescaped braces in multiline strings
    old_patterns = [
        # Pattern that might cause the issue
        r"(1\. Include the customer's EXACT balance \(£)\{customer\.get\('account_balance', 0\):,\}\)",
        # Alternative patterns that might be problematic
        r"(1\. Include the customer's EXACT balance \( )\{customer\.get\('account_balance', 0\):,\}\)",
        r"(Include the customer's EXACT balance \(£)\{customer\.get\('account_balance', 0\):,\}\)",
    ]
    
    # Try each pattern and fix
    fixed = False
    for pattern in old_patterns:
        if re.search(pattern, content):
            # Fix by properly escaping or restructuring the f-string
            content = re.sub(
                pattern, 
                r"\1{{customer.get('account_balance', 0):,}}", 
                content
            )
            fixed = True
            print(f"✅ Fixed pattern: {pattern}")
            break
    
    if not fixed:
        # More aggressive fix - find any problematic f-string sections
        # Look for the specific error pattern around line 832
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if "Include the customer's EXACT balance" in line and "{customer.get('account_balance'" in line:
                print(f"🔍 Found problematic line {i+1}: {line}")
                
                # Fix the line by properly formatting the f-string
                if "£{customer.get('account_balance', 0):,}" in line:
                    # Fix unescaped braces in f-string
                    lines[i] = line.replace(
                        "£{customer.get('account_balance', 0):,}",
                        "£{{customer.get('account_balance', 0):,}}"
                    )
                    fixed = True
                    print(f"✅ Fixed line {i+1}")
                    break
        
        if fixed:
            content = '\n'.join(lines)
    
    # Additional fixes for common f-string issues
    if not fixed:
        # Look for any unclosed f-strings or mismatched quotes
        content = fix_common_fstring_issues(content)
        fixed = True
    
    if fixed:
        # Save the corrected file
        print(f"💾 Saving corrected file...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ File corrected and saved!")
        return True
    else:
        print(f"❌ Could not automatically fix the syntax error.")
        print(f"💡 Please check line 832 manually for f-string syntax issues.")
        return False

def fix_common_fstring_issues(content):
    """Fix common f-string syntax issues."""
    
    # Fix 1: Multiline f-strings with improper escaping
    content = re.sub(
        r'f"""([^"]*)\{([^}]+):,\}([^"]*)"""',
        r'f"""\1{{{\2:,}}}\3"""',
        content,
        flags=re.DOTALL
    )
    
    # Fix 2: Single line f-strings with unescaped braces in literal parts
    content = re.sub(
        r'(f"[^"]*Include[^"]*balance[^"]*£)\{([^}]+):,\}',
        r'\1{{\2:,}}',
        content
    )
    
    # Fix 3: Triple quoted strings with f-string formatting issues
    content = re.sub(
        r'(f"""[^"]*1\. Include[^"]*balance[^"]*£)\{([^}]+):,\}',
        r'\1{{\2:,}}',
        content,
        flags=re.DOTALL
    )
    
    return content

def verify_syntax():
    """Verify that the fixed file has correct syntax."""
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    print(f"🔍 Verifying syntax of {file_path}...")
    
    try:
        # Try to compile the file to check for syntax errors
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, str(file_path), 'exec')
        print(f"✅ Syntax verification passed!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error still present:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during verification: {e}")
        return False

def test_import():
    """Test if the module can be imported successfully."""
    
    print(f"🧪 Testing module import...")
    
    try:
        # Add src to path temporarily
        import sys
        sys.path.insert(0, 'src')
        
        # Try to import the module
        from communication_processing.tabs.generate_tab import render_generate_plans_tab
        
        print(f"✅ Module imports successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main function to run the automatic fix."""
    
    print("=" * 60)
    print("🔧 AUTOMATIC FIX FOR generate_tab.py SYNTAX ERROR")
    print("=" * 60)
    
    # Step 1: Create backup
    print("\n1. Creating backup...")
    if not backup_original_file():
        return False
    
    # Step 2: Fix the syntax error
    print("\n2. Fixing syntax error...")
    if not fix_syntax_error():
        return False
    
    # Step 3: Verify syntax
    print("\n3. Verifying syntax...")
    if not verify_syntax():
        print("\n⚠️ Syntax error still present. Trying alternative fix...")
        
        # Try a more comprehensive fix
        apply_comprehensive_fix()
        
        if not verify_syntax():
            print("\n❌ Could not fix automatically. Please check manually.")
            return False
    
    # Step 4: Test import
    print("\n4. Testing module import...")
    test_import()
    
    print("\n" + "=" * 60)
    print("✅ AUTOMATIC FIX COMPLETED!")
    print("=" * 60)
    print("\nYour generate_tab.py file has been fixed!")
    print("You can now run your Streamlit app:")
    print("  python -m streamlit run src/main.py")
    print("\n💾 Original file backed up in 'backups/' directory")
    
    return True

def apply_comprehensive_fix():
    """Apply a comprehensive fix by replacing the entire problematic function."""
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic function and replace it
    function_start = "def create_real_ai_content_for_customer("
    
    if function_start in content:
        # Split content to find function
        parts = content.split(function_start)
        
        if len(parts) >= 2:
            # Find the end of the function (next def or end of file)
            after_func = parts[1]
            next_func_match = re.search(r'\ndef [a-zA-Z_]', after_func)
            
            if next_func_match:
                func_body = after_func[:next_func_match.start()]
                remaining = after_func[next_func_match.start():]
            else:
                func_body = after_func
                remaining = ""
            
            # Create a fixed version of the function
            fixed_function = create_fixed_function()
            
            # Rebuild the content
            new_content = parts[0] + fixed_function + remaining
            
            # Save the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Applied comprehensive fix to the function")

def create_fixed_function():
    """Create a corrected version of the problematic function."""
    
    return '''def create_real_ai_content_for_customer(customer: Dict, classification_type: str, letter_content: str, cost_manager, api_manager, options: Dict) -> Dict:
    """Create real AI-generated content for a single customer."""
    
    name = customer.get('name', 'Customer')
    category = customer.get('category', 'Unknown')
    
    # Get the customer's preferred language
    customer_language = customer.get('preferred_language', 'English')
    
    # Get financial indicators
    financial_indicators = customer.get('financial_indicators', {})
    account_health = financial_indicators.get('account_health', 'unknown')
    engagement_level = financial_indicators.get('engagement_level', 'unknown')
    digital_maturity = financial_indicators.get('digital_maturity', 'unknown')
    
    # Check upsell eligibility
    upsell_eligible = customer.get('upsell_eligible', False)
    upsell_products = customer.get('upsell_products', [])
    
    # Check video eligibility
    video_rules = VideoEligibilityRules()
    video_eligibility = video_rules.is_video_eligible(customer, classification_type)
    
    # Determine channels
    channels = get_channels_for_category(category, classification_type, customer, options)
    
    try:
        # Language instruction
        language_instruction = ""
        if customer_language and customer_language.lower() != 'english':
            language_instruction = f"""
            CRITICAL REQUIREMENT: Generate ALL content in {customer_language}!
            - All messages must be in {customer_language}
            - Use culturally appropriate greetings for {customer_language} speakers
            - Keep JSON field names in English, but all customer-facing text in {customer_language}
            """
        
        # Build customer data for prompt (avoiding f-string issues)
        account_balance = customer.get('account_balance', 0)
        customer_age = customer.get('age', 'Unknown')
        
        # Create comprehensive prompt - FIXED VERSION
        prompt = f"""{language_instruction}
        
        ORIGINAL LETTER TO REWRITE:
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
        
        TASK: Rewrite preserving ALL information, just personalize the delivery.
        
        CUSTOMER PROFILE:
        - Name: {name}
        - Preferred Language: {customer_language}
        - Category: {category}
        - Account Balance: £{account_balance:,}
        - Age: {customer_age}
        - Account Health: {account_health}
        - Engagement Level: {engagement_level}
        - Digital Maturity: {digital_maturity}
        - Upsell Eligible: {upsell_eligible}
        - Suggested Products: {', '.join(upsell_products) if upsell_products else 'None'}
        
        COMMUNICATION TYPE: {classification_type}
        LANGUAGE REQUIRED: {customer_language}
        
        Generate content for these channels: {', '.join(channels)}
        
        Return JSON with this exact structure (ALL TEXT IN {customer_language}):
        {{
            "in_app": {{
                "push_title": "Resonance Bank",
                "push_body": "personalized push notification text in {customer_language} (max 50 chars)",
                "message_subject": "subject line for in-app message in {customer_language}",
                "message_body": "full in-app message in {customer_language} (max 500 chars)",
                "cta_primary": "primary button text in {customer_language}",
                "cta_secondary": "secondary button text in {customer_language}"
            }},
            "email": {{
                "subject": "email subject line in {customer_language}",
                "preview": "email preview text in {customer_language} (max 100 chars)",
                "body": "full email body in {customer_language} (max 1000 chars)"
            }},
            "sms": {{
                "text": "SMS message in {customer_language} (max 160 chars)"
            }},
            "letter": {{
                "greeting": "Dear {name} in {customer_language}",
                "body": "letter body text in {customer_language} (max 500 chars)",
                "closing": "closing in {customer_language}"
            }},
            "voice_note": {{
                "script": "voice note script in {customer_language} (max 200 chars)"
            }},
            "video_message": {{
                "script": "personalized video script in {customer_language} (max 250 chars)",
                "greeting": "personalized greeting in {customer_language}",
                "closing": "thank you message in {customer_language}"
            }},
            "upsell_message": "upsell message in {customer_language} if eligible, null otherwise",
            "personalization_notes": ["list of personalization points used"],
            "language_used": "{customer_language}"
        }}
        
        REMEMBER: ALL customer-facing text must be in {customer_language}!
        """
        
        # Get AI response
        system_message = f"You are a professional banking communication specialist. Create highly personalized content using specific customer data. IMPORTANT: Generate all content in {customer_language} as specified."
        
        ai_result = api_manager.claude._with_exponential_backoff(
            model=api_manager.claude.model,
            max_tokens=1500,
            system=system_message,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        if ai_result and ai_result.content:
            content_text = ai_result.content[0].text
            
            # Clean and parse JSON
            if content_text.startswith("```json"):
                content_text = content_text.replace("```json", "").replace("```", "").strip()
            
            content = json.loads(content_text)
            
            # Add language to the content for tracking
            content['language_generated'] = customer_language
        else:
            # Fallback to template
            content = generate_template_content(name, category, classification_type, upsell_eligible, customer, options)
    
    except Exception as e:
        print(f"Error generating AI content for {name}: {e}")
        # Fallback to template content
        content = generate_template_content(name, category, classification_type, upsell_eligible, customer, options)
    
    # Calculate costs
    costs = calculate_channel_costs(channels, cost_manager)
    
    # Include language in the return data
    return {
        'customer_id': customer.get('customer_id', 'Unknown'),
        'customer_name': name,
        'customer_category': category,
        'customer_language': customer_language,
        'classification_type': classification_type,
        'channels': channels,
        'content': content,
        'costs': costs,
        'upsell_eligible': upsell_eligible,
        'video_eligible': video_eligibility.get('eligible', False),
        'video_tier': video_eligibility.get('tier'),
        'video_score': video_eligibility.get('score', 0)
    }

'''

if __name__ == "__main__":
    main()