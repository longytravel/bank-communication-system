"""
Fix the letter content issue - SAFELY with backups
This will make the system ACTUALLY rewrite letters for each customer
"""

import shutil
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('src')

def backup_files():
    """Backup critical files before making changes."""
    
    print("🛡️ Creating backups...")
    
    backup_dir = Path("backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_backup = [
        "src/communication_processing/tabs/generate_tab.py",
        "src/communication_processing/customer_plans_ui.py",
        "src/api/claude_api.py"
    ]
    
    for file_path in files_to_backup:
        source = Path(file_path)
        if source.exists():
            dest = backup_dir / file_path.replace("/", "_")
            shutil.copy2(source, dest)
            print(f"  ✅ Backed up: {file_path}")
    
    print(f"\n📁 Backups saved to: {backup_dir}")
    return backup_dir

def create_fixed_generate_function():
    """Create the FIXED version of the generate function."""
    
    print("\n📝 Creating fixed generate function...")
    
    # This is the CORRECTED function that actually uses letter content
    fixed_code = '''"""
FIXED VERSION - Actually uses letter content!
Add this to generate_tab.py
"""

def create_real_ai_content_for_customer_FIXED(
    customer: Dict, 
    classification_type: str, 
    letter_content: str,  # NEW: ACTUAL LETTER CONTENT
    cost_manager, 
    api_manager, 
    options: Dict
) -> Dict:
    """Create real AI-generated content by REWRITING the letter for each customer."""
    
    name = customer.get('name', 'Customer')
    category = customer.get('category', 'Unknown')
    customer_language = customer.get('preferred_language', 'English')
    
    # Get financial indicators
    financial_indicators = customer.get('financial_indicators', {})
    account_health = financial_indicators.get('account_health', 'unknown')
    engagement_level = financial_indicators.get('engagement_level', 'unknown')
    digital_maturity = financial_indicators.get('digital_maturity', 'unknown')
    
    # Check eligibilities
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
            CRITICAL: ALL content must be in {customer_language}!
            - Translate everything to {customer_language}
            - Use culturally appropriate tone for {customer_language} speakers
            """
        
        # THE KEY FIX: Include the ACTUAL LETTER CONTENT in the prompt!
        prompt = f"""
        {language_instruction}
        
        ORIGINAL LETTER TO REWRITE:
        ========================================
        {letter_content}
        ========================================
        
        TASK: Rewrite this letter for this specific customer across multiple channels.
        Keep the same core information but make it completely personalized.
        
        CUSTOMER PROFILE:
        - Name: {name}
        - Preferred Language: {customer_language}
        - Category: {category}
        - Account Balance: £{customer.get('account_balance', 0):,}
        - Age: {customer.get('age', 'Unknown')}
        - Account Health: {account_health}
        - Engagement Level: {engagement_level}
        - Digital Maturity: {digital_maturity}
        - Upsell Eligible: {upsell_eligible}
        - Suggested Products: {', '.join(upsell_products) if upsell_products else 'None'}
        
        REQUIREMENTS:
        1. Rewrite the letter content for each channel below
        2. Keep the same information but make it engaging and personal
        3. Use the customer's name and reference their specific situation
        4. Adapt length and tone for each channel
        5. For SMS: Maximum 160 characters
        6. For Email: Professional but friendly
        7. For In-app: Direct and actionable
        
        Generate content for these channels: {', '.join(channels)}
        
        Return JSON with personalized versions of the LETTER CONTENT:
        {{
            "in_app": {{
                "push_title": "Resonance Bank",
                "push_body": "personalized version in {customer_language} (max 50 chars)",
                "message_subject": "subject based on letter content in {customer_language}",
                "message_body": "personalized letter content for in-app in {customer_language} (max 500 chars)",
                "cta_primary": "action button in {customer_language}",
                "cta_secondary": "secondary action in {customer_language}"
            }},
            "email": {{
                "subject": "email subject from letter in {customer_language}",
                "preview": "preview of letter content in {customer_language} (max 100 chars)",
                "body": "full personalized letter rewritten for email in {customer_language} (max 1000 chars)"
            }},
            "sms": {{
                "text": "letter content condensed to SMS in {customer_language} (max 160 chars)"
            }},
            "letter": {{
                "greeting": "Dear {name} in {customer_language}",
                "body": "personalized letter body in {customer_language} (rewritten from original)",
                "closing": "appropriate closing in {customer_language}"
            }},
            "voice_note": {{
                "script": "spoken version of letter in {customer_language} (max 200 chars)"
            }},
            "upsell_message": "upsell based on letter context if eligible, null otherwise",
            "personalization_notes": ["list of how letter was personalized"]
        }}
        
        REMEMBER: Rewrite the ACTUAL LETTER CONTENT for this customer!
        """
        
        # Get AI response
        system_message = f"""You are a banking communication specialist. 
        Your job is to take generic letters and rewrite them to be completely personalized for each customer.
        The rewritten content must convey the same information as the original letter but in a way that resonates with the specific customer.
        ALL content must be in {customer_language}."""
        
        ai_result = api_manager.claude._with_exponential_backoff(
            model=api_manager.claude.model,
            max_tokens=2000,
            system=system_message,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4  # Slightly higher for more creative rewrites
        )
        
        if ai_result and ai_result.content:
            content_text = ai_result.content[0].text
            
            # Clean and parse JSON
            if content_text.startswith("```json"):
                content_text = content_text.replace("```json", "").replace("```", "").strip()
            
            content = json.loads(content_text)
            content['language_generated'] = customer_language
            content['letter_was_rewritten'] = True  # Flag to verify it worked
        else:
            # Fallback
            content = generate_template_content(name, category, classification_type, upsell_eligible, customer, options)
            content['letter_was_rewritten'] = False
    
    except Exception as e:
        print(f"Error rewriting letter for {name}: {e}")
        content = generate_template_content(name, category, classification_type, upsell_eligible, customer, options)
        content['letter_was_rewritten'] = False
    
    # Calculate costs
    costs = calculate_channel_costs(channels, cost_manager)
    
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
        'video_score': video_eligibility.get('score', 0),
        'letter_rewritten': content.get('letter_was_rewritten', False)  # Track if it worked
    }
'''
    
    # Save the fixed function to a file
    output_file = Path("fixed_generate_function.py")
    output_file.write_text(fixed_code)
    
    print(f"✅ Fixed function saved to: {output_file}")
    print("\nThe fix includes:")
    print("  1. ✅ Letter content parameter added")
    print("  2. ✅ Letter included in Claude prompt")
    print("  3. ✅ Instructions to rewrite for each customer")
    print("  4. ✅ Tracking flag to verify it worked")
    
    return output_file

if __name__ == "__main__":
    print("=" * 60)
    print("FIXING THE LETTER CONTENT ISSUE")
    print("=" * 60)
    
    # Step 1: Backup
    backup_dir = backup_files()
    
    # Step 2: Create fixed function
    fixed_file = create_fixed_generate_function()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Review the fixed function in: fixed_generate_function.py")
    print("2. We'll integrate it into generate_tab.py")
    print("3. We'll update the calling code to pass letter content")
    print("4. Test with our 3 test customers")
    print("\n🛡️ Your backups are safe in:", backup_dir)
    print("\nReady to apply the fix? (We can always restore from backup)")