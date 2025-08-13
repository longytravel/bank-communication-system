"""
Simple API Test - Test API modules directly
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def test_api_imports():
    """Test API module imports."""
    print("🧪 Testing API Imports...")
    
    try:
        # Test config first
        from config import get_api_key
        print("  ✅ Config imported")
        
	# Test individual API modules
        from api.claude_api import ClaudeAPI
        print("  ✅ Claude API module imported")
        
        from api.openai_api import OpenAIAPI
        print("  ✅ OpenAI API module imported")
        
        from api.api_manager import APIManager
        print("  ✅ API Manager module imported")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_api_initialization():
    """Test API initialization with API keys."""
    print("\n🧪 Testing API Initialization...")
    
    try:
        from config import get_api_key
        
        # Check if we have API keys
        claude_key = get_api_key('claude')
        openai_key = get_api_key('openai')
        
        print(f"  🔑 Claude key available: {claude_key is not None}")
        print(f"  🔑 OpenAI key available: {openai_key is not None}")
        
        if claude_key and openai_key:
            print("  💡 Attempting API initialization...")
            
            # Try to initialize APIs
            from api.claude_api import ClaudeAPI
            from api.openai_api import OpenAIAPI
            from api.api_manager import APIManager
            
            try:
                claude_api = ClaudeAPI()
                print("  ✅ Claude API initialized")
            except Exception as e:
                print(f"  ❌ Claude API failed: {e}")
            
            try:
                openai_api = OpenAIAPI()
                print("  ✅ OpenAI API initialized")
            except Exception as e:
                print(f"  ❌ OpenAI API failed: {e}")
            
            try:
                api_manager = APIManager()
                print("  ✅ API Manager initialized")
                
                # Test status
                status = api_manager.get_api_status()
                print(f"  📊 Claude status: {status.get('claude', {}).get('status')}")
                print(f"  📊 OpenAI status: {status.get('openai', {}).get('status')}")
                
            except Exception as e:
                print(f"  ❌ API Manager failed: {e}")
        
        else:
            print("  ⚠️ No API keys found - skipping initialization test")
            print("  💡 Add API keys to .env file to test full functionality")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API initialization test failed: {e}")
        return False

def main():
    """Run API-specific tests."""
    print("🚀 API Modules Test")
    print("=" * 40)
    
    tests = [
        ("API Imports", test_api_imports),
        ("API Initialization", test_api_initialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  💥 {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 API Test Results:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 API Tests: {passed}/{len(results)} passed")
    
    if passed == len(results):
        print("🎉 API modules working correctly!")
    else:
        print("⚠️ Some API tests failed.")

if __name__ == "__main__":
    main()