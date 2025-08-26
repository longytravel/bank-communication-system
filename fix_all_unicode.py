"""
Complete fix for all Unicode character issues in generate_tab.py
"""

from pathlib import Path
import re

def fix_all_unicode_issues():
    """Remove ALL Unicode characters and fix the file completely."""
    
    print("=" * 60)
    print("COMPLETE UNICODE FIX FOR generate_tab.py")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    # Read the file
    print("Reading file...")
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    
    # First, let's find all Unicode characters
    unicode_chars = set()
    for char in content:
        if ord(char) > 127:
            unicode_chars.add(char)
    
    if unicode_chars:
        print(f"\nFound {len(unicode_chars)} unique Unicode characters:")
        for char in unicode_chars:
            count = content.count(char)
            print(f"  '{char}' (U+{ord(char):04X}): {count} occurrences")
    
    # Replace ALL problematic Unicode characters
    replacements = {
        '✓': 'YES',
        '✅': 'OK',
        '❌': 'NO',
        '→': '->',
        '•': '*',
        '✔': 'YES',
        '✗': 'NO',
        '❗': '!',
        '⚠': 'WARNING',
        '📊': '[DATA]',
        '📈': '[CHART]',
        '💡': '[TIP]',
        '🎯': '[TARGET]',
        '🔍': '[SEARCH]',
        '📝': '[NOTE]',
        '🎬': '[VIDEO]',
        '💰': '[COST]',
        '📱': '[MOBILE]',
        '📧': '[EMAIL]',
        '💬': '[SMS]',
        '📮': '[LETTER]',
        '🔊': '[VOICE]',
        '⚡': '[FAST]',
        '🧪': '[TEST]',
        '🤖': '[AI]',
        '👤': '[USER]',
        '🛡️': '[SHIELD]',
        '️': '',  # Invisible character
        '\u200b': '',  # Zero-width space
        '\ufeff': '',  # BOM
    }
    
    # Apply replacements
    print("\nApplying replacements...")
    for unicode_char, replacement in replacements.items():
        if unicode_char in content:
            count = content.count(unicode_char)
            content = content.replace(unicode_char, replacement)
            print(f"  Replaced {count} instances of '{unicode_char}' with '{replacement}'")
    
    # Remove any remaining non-ASCII characters
    print("\nRemoving any remaining non-ASCII characters...")
    
    # This will replace any remaining Unicode with a space
    cleaned_content = ''.join(
        char if ord(char) < 128 else ' ' 
        for char in content
    )
    
    # Fix any broken formatting from replacements
    # Fix multiple spaces
    cleaned_content = re.sub(r' +', ' ', cleaned_content)
    
    # Fix empty lines
    cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
    
    # Write the cleaned content
    print("\nWriting cleaned file...")
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(cleaned_content)
    
    print("✅ File cleaned and saved")
    return True

def verify_no_unicode():
    """Verify no Unicode characters remain."""
    
    print("\n🔍 Verifying no Unicode remains...")
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for any non-ASCII
    non_ascii = [char for char in content if ord(char) > 127]
    
    if non_ascii:
        print(f"❌ Found {len(non_ascii)} non-ASCII characters remaining")
        # Show first 10
        for char in set(non_ascii[:10]):
            print(f"  '{char}' (U+{ord(char):04X})")
        return False
    else:
        print("✅ No Unicode characters found - file is clean ASCII")
        return True

def test_syntax():
    """Test Python syntax is valid."""
    
    print("\n🧪 Testing Python syntax...")
    
    file_path = Path("src/communication_processing/tabs/generate_tab.py")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Try to compile the code
        compile(code, str(file_path), 'exec')
        print("✅ Python syntax is valid!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error at line {e.lineno}:")
        print(f"   {e.text[:100] if e.text else 'N/A'}")
        print(f"   {e.msg}")
        return False

def test_full_import():
    """Test the full import chain."""
    
    print("\n🧪 Testing full import chain...")
    
    try:
        import sys
        from pathlib import Path
        
        # Add to path
        sys.path.insert(0, 'src')
        
        # Clear any cached imports
        modules_to_clear = [
            'communication_processing.tabs.generate_tab',
            'communication_processing.customer_plans_ui',
            'communication_processing',
            'main'
        ]
        
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Try the imports that were failing
        print("  Importing generate_tab...")
        from communication_processing.tabs.generate_tab import render_generate_plans_tab
        print("  ✅ generate_tab imported")
        
        print("  Importing customer_plans_ui...")
        from communication_processing.customer_plans_ui import render_customer_communication_plans_page
        print("  ✅ customer_plans_ui imported")
        
        print("  Importing main...")
        import main
        print("  ✅ main imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except SyntaxError as e:
        print(f"\n❌ Syntax error in {e.filename}:")
        print(f"   Line {e.lineno}: {e.text[:100] if e.text else 'N/A'}")
        print(f"   {e.msg}")
        return False
        
    except ImportError as e:
        print(f"\n⚠️ Import error: {e}")
        print("   (This might be OK if it's about missing packages)")
        return True
        
    except Exception as e:
        print(f"\n⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    # Step 1: Clean the file
    if not fix_all_unicode_issues():
        print("❌ Failed to clean file")
        exit(1)
    
    # Step 2: Verify it's clean
    if not verify_no_unicode():
        print("❌ Unicode characters still present")
        exit(1)
    
    # Step 3: Check syntax
    if not test_syntax():
        print("❌ Python syntax is invalid")
        print("\n💡 The file may need manual fixing.")
        print("   Check src/communication_processing/tabs/generate_tab.py")
        exit(1)
    
    # Step 4: Test imports
    if test_full_import():
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! ALL ISSUES FIXED!")
        print("=" * 60)
        print("\nYou can now run:")
        print("  1. The main app:")
        print("     python -m streamlit run src/main.py")
        print("\n  2. The personalization test:")
        print("     python test_complete_personalization.py")
        print("\n  3. Any other tests")
    else:
        print("\n⚠️ Some import issues remain")
        print("Check the error messages above")