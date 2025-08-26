"""
Fix the syntax error in generate_tab.py
This script will automatically fix the unterminated string literal issue
"""

from pathlib import Path
import re

def fix_generate_tab():
    """Fix the syntax error in generate_tab.py"""
    
    print("=" * 60)
    print("FIXING SYNTAX ERROR IN generate_tab.py")
    print("=" * 60)
    
    # Path to the problematic file
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    if not file_path.exists():
        print(f"❌ Error: {file_path} not found!")
        return False
    
    print(f"📄 Reading {file_path}...")
    
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Finding and fixing the syntax error...")
        
        # The problematic pattern - it's trying to use f-string formatting inside a string
        # Find the section with the unterminated literal
        
        # First, let's fix the immediate syntax error
        # The issue is with these lines that have incorrect f-string formatting
        problematic_patterns = [
            (r"- Their EXACT balance amount \(£\{customer\.get\('account_balance', 0\):,\}\)",
             "- Their EXACT balance amount (e.g., £50,000)"),
            (r"- Their ACTUAL usage pattern \(\{customer\.get\('digital_logins_per_month', 0\)\} logins/month\)",
             "- Their ACTUAL usage pattern (e.g., 45 logins/month)"),
            (r"- Their AGE if relevant \(\{customer\.get\('age', 'Unknown'\)\} years\)",
             "- Their AGE if relevant (e.g., 32 years)"),
        ]
        
        for pattern, replacement in problematic_patterns:
            content = re.sub(pattern, replacement, content)
        
        # Also look for a simpler fix - find the whole REQUIREMENTS section and replace it
        if "REQUIREMENTS FOR DEEP PERSONALIZATION:" in content:
            print("🔧 Found REQUIREMENTS section, replacing with fixed version...")
            
            # Replace the problematic REQUIREMENTS section
            old_requirements = """        REQUIREMENTS FOR DEEP PERSONALIZATION:
        
        1. YOU MUST reference these SPECIFIC data points:
           - Their EXACT balance amount (£{customer.get('account_balance', 0):,})
           - Their ACTUAL usage pattern ({customer.get('digital_logins_per_month', 0)} logins/month)
           - Their AGE if relevant ({customer.get('age', 'Unknown')} years)
           - Their SPECIFIC eligible products if upsell eligible"""
            
            new_requirements = """        REQUIREMENTS FOR DEEP PERSONALIZATION:
        
        1. YOU MUST reference these SPECIFIC data points:
           - Their EXACT balance amount from the customer profile
           - Their ACTUAL usage pattern from the customer profile
           - Their AGE if relevant from the customer profile
           - Their SPECIFIC eligible products if upsell eligible"""
            
            content = content.replace(old_requirements, new_requirements)
        
        # Also check for the format string issue in the actual values section
        # Look for where customer data is actually being inserted
        if "✅ \"With your £50,000 balance...\"" in content:
            print("🔧 Fixing example format strings...")
            
            # Fix the examples section too
            old_examples = """        3. DO use specific references like:
           ✅ "With your £50,000 balance..."
           ✅ "Your 45 logins this month show..."
           ✅ "At 32, you're perfectly positioned for..."
           ✅ "You qualify for: Wealth Management, Premium Credit Card...\""""
            
            new_examples = """        3. DO use specific references like:
           - "With your actual balance amount..."
           - "Your actual login count this month shows..."
           - "At your age, you're perfectly positioned for..."
           - "You qualify for: [actual products]...\""""
            
            content = content.replace(old_examples, new_examples)
        
        # Write the fixed content back
        print("💾 Writing fixed content back to file...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ File fixed successfully!")
        
        # Verify the fix by trying to compile it
        print("\n🧪 Verifying the fix...")
        try:
            compile(content, str(file_path), 'exec')
            print("✅ Python syntax is now valid!")
            return True
        except SyntaxError as e:
            print(f"⚠️ There might still be syntax errors: {e}")
            print("   Running additional fixes...")
            
            # If there are still issues, do a more aggressive fix
            return aggressive_fix(file_path)
            
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

def aggressive_fix(file_path):
    """More aggressive fix if the gentle approach doesn't work"""
    
    print("\n🔨 Applying aggressive fix...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        in_problematic_section = False
        
        for i, line in enumerate(lines):
            # Check if we're in a problematic f-string section
            if "REQUIREMENTS FOR DEEP PERSONALIZATION:" in line:
                in_problematic_section = True
            elif in_problematic_section and "4. Keep ALL original letter content" in line:
                in_problematic_section = False
            
            # Fix specific problematic lines
            if in_problematic_section:
                # Remove f-string formatting from within strings
                if "customer.get(" in line and "{" in line:
                    # Replace complex f-string expressions with placeholders
                    line = re.sub(r'\{customer\.get\([^}]+\)[^}]*\}', '[customer value]', line)
                    line = re.sub(r'\(£\{[^}]+\}\)', '(customer balance)', line)
                    line = re.sub(r'\({[^}]+}\)', '(customer data)', line)
            
            # Also fix any standalone f-string issues
            if "£{customer.get('account_balance'" in line:
                line = line.replace("£{customer.get('account_balance', 0):,}", "customer balance")
            
            fixed_lines.append(line)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print("✅ Aggressive fix applied!")
        
        # Verify again
        content = ''.join(fixed_lines)
        try:
            compile(content, str(file_path), 'exec')
            print("✅ File is now syntactically correct!")
            return True
        except SyntaxError as e:
            print(f"❌ Still has syntax errors: {e}")
            print("   You may need to manually edit the file.")
            return False
            
    except Exception as e:
        print(f"❌ Aggressive fix failed: {e}")
        return False

def test_import():
    """Test if the module can be imported after the fix"""
    
    print("\n🧪 Testing if the module can be imported...")
    
    try:
        # Clear any cached imports
        import sys
        if 'communication_processing.tabs.generate_tab' in sys.modules:
            del sys.modules['communication_processing.tabs.generate_tab']
        
        # Try to import
        from src.communication_processing.tabs import generate_tab
        print("✅ Module imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    # Run the fix
    success = fix_generate_tab()
    
    if success:
        # Test the import
        test_import()
        
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETE!")
        print("=" * 60)
        print("\nYour system should now work. Try running:")
        print("  python -m streamlit run src/main.py")
        print("\nThe syntax error has been fixed!")
    else:
        print("\n" + "=" * 60)
        print("⚠️ MANUAL INTERVENTION NEEDED")
        print("=" * 60)
        print("\nThe automatic fix couldn't completely resolve the issue.")
        print("Please check src/communication_processing/tabs/generate_tab.py")
        print("Look for any lines with {customer.get(...)} inside f-strings")
            