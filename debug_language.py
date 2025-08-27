"""
IMMEDIATE DEBUG - Find where Polish gets lost
Run this NOW to identify the issue
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

def check_1_csv_data():
    """Check if CSV has language set."""
    import pandas as pd
    
    print("\n🔍 CHECK 1: CSV Data")
    print("-" * 40)
    
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    if not csv_path.exists():
        print(f"❌ CSV not found at {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    
    # Check columns
    if 'preferred_language' not in df.columns:
        print("❌ PROBLEM: 'preferred_language' column doesn't exist!")
        print(f"Columns: {list(df.columns)}")
        return False
    
    # Check Polish customers
    polish_found = False
    for idx, row in df.iterrows():
        name = row.get('name', '')
        if 'Stanisław' in name or 'Kowalski' in name:
            lang = row.get('preferred_language', 'MISSING')
            print(f"✓ Found: {name}")
            print(f"  Language: {lang}")
            if lang in ['Polish', 'polish', 'pl', 'PL']:
                print("  ✅ Language is set to Polish")
                polish_found = True
            else:
                print(f"  ❌ Language is '{lang}' not Polish!")
                return False
    
    if not polish_found:
        print("❌ No Polish customers found in CSV")
        return False
    
    return True

def check_2_api_manager():
    """Check if api_manager preserves language."""
    print("\n🔍 CHECK 2: API Manager")
    print("-" * 40)
    
    try:
        from api.api_manager import APIManager
        
        # Check the code
        import inspect
        source = inspect.getsource(APIManager.analyze_customer_base)
        
        if 'preferred_language' in source:
            print("✅ API Manager mentions 'preferred_language'")
            
            # Check if it's preserved
            if "factual_fields" in source and "preferred_language" in source:
                print("✅ Language is in preservation list")
            elif "original_customer[field]" in source:
                print("⚠️ Generic preservation - should work")
            else:
                print("❌ Language might not be preserved properly")
        else:
            print("❌ API Manager doesn't handle 'preferred_language'")
            
    except Exception as e:
        print(f"❌ Error checking API Manager: {e}")
        return False
    
    return True

def check_3_claude_prompt():
    """Check if Claude receives language instruction."""
    print("\n🔍 CHECK 3: Claude Prompt")
    print("-" * 40)
    
    try:
        from api.claude_api import ClaudeAPI
        import inspect
        
        source = inspect.getsource(ClaudeAPI._build_letter_processing_prompt)
        
        checks = {
            "Gets language from profile": "profile.get('preferred_language'" in source,
            "Includes in prompt": "customer_language" in source or "preferred_language" in source,
            "Polish-specific instructions": "'Polish'" in source or "'polish'" in source,
            "Critical instruction": "CRITICAL" in source
        }
        
        for check, passed in checks.items():
            if passed:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                
        if not all(checks.values()):
            print("\n⚠️ Claude prompt may not be strong enough")
            
    except Exception as e:
        print(f"❌ Error checking Claude: {e}")
        return False
    
    return True

def test_direct_claude_call():
    """Test Claude directly with a Polish customer."""
    print("\n🧪 DIRECT TEST: Claude with Polish customer")
    print("-" * 40)
    
    try:
        from api.claude_api import ClaudeAPI
        
        claude = ClaudeAPI()
        
        # Explicit Polish customer
        test_customer = {
            'customer_id': 'TEST_POLISH',
            'name': 'Test Kowalski',
            'preferred_language': 'Polish',  # EXPLICITLY POLISH
            'category': 'Digital-first self-serve',
            'account_balance': 25000
        }
        
        print(f"Sending to Claude: {test_customer}")
        
        result = claude.process_customer_letter(
            letter_text="Important terms update",
            customer_profile=test_customer,
            allowed_channels=['email']
        )
        
        if result and 'personalized_content' in result:
            email = result.get('personalized_content', {}).get('email', {})
            body = email.get('body', '')[:200]
            
            print(f"\nClaude returned:")
            print(f"Body: {body[:100]}...")
            
            polish_indicators = ['Szanown', 'Panie', 'Pani', 'dziękujemy', 'prosimy']
            if any(word in body for word in polish_indicators):
                print("✅ Claude generated Polish content!")
            else:
                print("❌ Claude still generating English!")
                print("\n⚠️ PROBLEM: Claude isn't following language instruction")
        else:
            print("❌ No result from Claude")
            
    except Exception as e:
        print(f"❌ Error testing Claude: {e}")
        
def fix_csv_immediately():
    """Emergency fix - ensure CSV has Polish set."""
    print("\n🔧 EMERGENCY FIX: Force update CSV")
    print("-" * 40)
    
    import pandas as pd
    
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        
        # Ensure column exists
        if 'preferred_language' not in df.columns:
            df['preferred_language'] = 'English'
            print("Added 'preferred_language' column")
        
        # Force update Stanisław
        updated = False
        for idx in df.index:
            if 'Stanisław' in str(df.loc[idx, 'name']) or 'Kowalski' in str(df.loc[idx, 'name']):
                df.loc[idx, 'preferred_language'] = 'Polish'
                df.loc[idx, 'name'] = 'Stanisław Kowalski'  # Ensure exact name
                print(f"✅ Updated row {idx}: {df.loc[idx, 'name']} -> Polish")
                updated = True
        
        if updated:
            # Save
            df.to_csv(csv_path, index=False)
            print(f"✅ Saved to {csv_path}")
            
            # Verify
            df2 = pd.read_csv(csv_path)
            polish = df2[df2['preferred_language'] == 'Polish']
            print(f"✅ Verified: {len(polish)} Polish customers in CSV")
        else:
            print("❌ Couldn't find Stanisław to update")

def main():
    print("=" * 60)
    print("LANGUAGE LOSS DETECTIVE")
    print("=" * 60)
    
    # Run all checks
    csv_ok = check_1_csv_data()
    api_ok = check_2_api_manager()
    claude_ok = check_3_claude_prompt()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    print("-" * 40)
    
    if not csv_ok:
        print("❌ PROBLEM: CSV doesn't have Polish set properly")
        print("   FIX: Running emergency CSV fix...")
        fix_csv_immediately()
        print("\n   ✅ CSV fixed. Restart Streamlit and try again.")
        
    elif not api_ok:
        print("❌ PROBLEM: API Manager not preserving language")
        print("   FIX: Update api_manager.py with the fixed version")
        
    elif not claude_ok:
        print("❌ PROBLEM: Claude not receiving language properly")
        print("   FIX: Update claude_api.py to strengthen prompt")
        
    else:
        print("⚠️ All checks passed but still English...")
        print("\nTesting Claude directly...")
        test_direct_claude_call()
        
        print("\n📋 POSSIBLE ISSUES:")
        print("1. Streamlit is caching old results - Clear cache")
        print("2. Claude model isn't following instructions - Need stronger prompt")
        print("3. There's a different CSV being used - Check file paths")

if __name__ == "__main__":
    main()
    
    print("\n\n🎯 IMMEDIATE ACTION:")
    print("1. Run this script: python debug_language.py")
    print("2. Note which check fails")
    print("3. Apply the suggested fix")
    print("4. Restart Streamlit: streamlit run src/main.py")
    print("5. Try generating for Stanisław again")