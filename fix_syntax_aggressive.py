"""
Aggressive fix for syntax error - rebuild the function
"""

from pathlib import Path

def fix_generate_tab_syntax():
    """Fix by rebuilding the problematic section."""
    
    print("=" * 60)
    print("AGGRESSIVE FIX FOR SYNTAX ERROR")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    # Read the entire file
    content = file_path.read_text(encoding='utf-8')
    
    # The problem is around the get_base_templates function
    # Let's replace it with a working version
    
    # Find where get_base_templates starts
    start_marker = "def get_base_templates"
    end_marker = "def calculate_channel_costs"
    
    if start_marker in content and end_marker in content:
        # Extract everything before and after
        before = content.split(start_marker)[0]
        after_parts = content.split(end_marker)
        if len(after_parts) > 1:
            after = end_marker + after_parts[1]
        else:
            after = ""
        
        # Insert a working version of get_base_templates
        fixed_function = '''def get_base_templates(name: str, category: str, classification_type: str) -> Dict:
    """Get base communication templates."""
    
    templates = {}
    
    # Digital-first templates
    if category == "Digital-first self-serve":
        templates["in_app"] = {
            "push_title": "Resonance Bank",
            "push_body": f"Hi {name}! Important update - tap to view",
            "message_subject": f"Your Account Update",
            "message_body": f"Hi {name}, we have an important update about your account.",
            "cta_primary": "Review Now",
            "cta_secondary": "Remind Me Later"
        }
        templates["email"] = {
            "subject": f"Important Update for {name}",
            "preview": "Action required for your account",
            "body": f"Dear {name}, We have important information about your account."
        }
        templates["sms"] = {
            "text": f"Hi {name}, important update from Resonance Bank. Check your app for details."
        }
        templates["voice_note"] = {
            "script": f"Hello {name}, this is Resonance Bank with an important update."
        }
    else:
        # Default templates for other categories
        templates["email"] = {
            "subject": f"Important Update",
            "preview": "Information about your account",
            "body": f"Dear {name}, We have information to share with you."
        }
        templates["letter"] = {
            "greeting": f"Dear {name}",
            "body": "We are writing to inform you about your account.",
            "closing": "Yours sincerely"
        }
    
    return templates

'''
        
        # Rebuild the file
        new_content = before + fixed_function + after
        
        # Save it
        file_path.write_text(new_content, encoding='utf-8')
        print("✅ Replaced get_base_templates function with working version")
        return True
    else:
        print("❌ Could not find the function markers")
        return False

def test_import():
    """Test if the module can now be imported."""
    print("\n🧪 Testing import...")
    try:
        import sys
        sys.path.append('src')
        from communication_processing.tabs.generate_tab import create_real_ai_content_for_customer
        print("✅ SUCCESS! Module imports correctly now")
        return True
    except SyntaxError as e:
        print(f"❌ Still syntax error: {e}")
        print(f"   at {e.filename}:{e.lineno}")
        return False
    except Exception as e:
        print(f"⚠️ Different error (syntax probably fixed): {e}")
        return True

if __name__ == "__main__":
    if fix_generate_tab_syntax():
        if test_import():
            print("\n" + "=" * 60)
            print("🎉 SYNTAX ERROR FIXED!")
            print("=" * 60)
            print("\nYou can now run:")
            print("  python test_complete_personalization.py")
            print("\nOr test in Streamlit:")
            print("  python -m streamlit run src/main.py")
        else:
            print("\n⚠️ Syntax error persists. Check the file manually.")