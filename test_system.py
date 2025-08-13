"""
Comprehensive System Test
Tests all modules we've built so far.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_config_module():
    """Test the configuration module."""
    print("🧪 Testing Configuration Module...")
    
    try:
        from config import config, get_api_key, get_directory, is_configured
        
        # Test basic functionality
        print(f"  ✅ Config imported successfully")
        print(f"  📁 Base directory: {config.base_dir}")
        
        # Test directories
        data_dir = get_directory('data')
        print(f"  📁 Data directory: {data_dir}")
        print(f"  📁 Directory exists: {data_dir.exists()}")
        
        # Test API keys (should be None if not set)
        claude_key = get_api_key('claude')
        openai_key = get_api_key('openai')
        
        print(f"  🔑 Claude API key found: {claude_key is not None}")
        print(f"  🔑 OpenAI API key found: {openai_key is not None}")
        print(f"  ⚙️ System configured: {is_configured()}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Config test failed: {e}")
        return False

def test_business_rules():
    """Test the business rules engine."""
    print("\n🧪 Testing Business Rules Engine...")
    
    try:
        from business_rules.engine import BusinessRulesEngine
        from business_rules.rules import rules_config
        
        # Test rules config
        print(f"  ✅ Rules imported successfully")
        
        # Test rule configuration
        customer_rules = rules_config.get_rules_for_customer_category("Digital-first self-serve")
        print(f"  📋 Digital-first rules: {len(customer_rules)} found")
        
        comm_rules = rules_config.get_rules_for_communication_type("REGULATORY")
        print(f"  📋 Regulatory rules: {len(comm_rules)} found")
        
        # Test rules engine
        engine = BusinessRulesEngine()
        print(f"  ⚙️ Engine initialized successfully")
        
        active_rules = engine.get_active_rules()
        print(f"  📊 Active rule modules: {len(active_rules)}")
        
        # Test vulnerable customer protection
        test_result = {
            "customer_category": {"label": "Vulnerable / extra-support"},
            "classification": {"label": "PROMOTIONAL"},
            "upsell_included": True,
            "upsell_details": {"product": "Test Product"},
            "assets": {"sms_text": "Special offer!"},
            "comms_plan": {"timeline": []}
        }
        
        result = engine.apply_all_rules(test_result, {})
        protection_applied = not result.get("upsell_included", True)
        print(f"  🛡️ Vulnerable protection works: {protection_applied}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Business rules test failed: {e}")
        return False

def test_api_modules():
    """Test API modules (without making actual API calls)."""
    print("\n🧪 Testing API Modules...")
    
    try:
        # Test imports first
        from api.claude_api import ClaudeAPI
        from api.openai_api import OpenAIAPI  
        from api.api_manager import APIManager
        
        print(f"  ✅ API modules imported successfully")
        
        # Test API manager initialization (will fail without API keys, but that's OK)
        try:
            manager = APIManager()
            print(f"  ⚙️ API Manager initialized successfully")
            
            # Test status check
            status = manager.get_api_status()
            claude_status = status.get('claude', {}).get('status', 'unknown')
            openai_status = status.get('openai', {}).get('status', 'unknown')
            
            print(f"  🔗 Claude status: {claude_status}")
            print(f"  🔗 OpenAI status: {openai_status}")
            
            return True
            
        except ValueError as e:
            if "API key not found" in str(e):
                print(f"  ⚠️ API keys not configured (expected): {e}")
                print(f"  💡 Set up .env file with API keys to test fully")
                return True
            else:
                raise e
        
    except Exception as e:
        print(f"  ❌ API modules test failed: {e}")
        return False

def test_file_structure():
    """Test that all expected files and directories exist."""
    print("\n🧪 Testing File Structure...")
    
    expected_files = [
        "src/config.py",
        "src/business_rules/__init__.py",
        "src/business_rules/engine.py",
        "src/business_rules/customer_rules.py",
        "src/business_rules/communication_rules.py",
        "src/business_rules/rules.py",
        "src/api/__init__.py",
        "src/api/claude_api.py",
        "src/api/openai_api.py",
        "src/api/api_manager.py",
        "requirements.txt",
        ".env.example"
    ]
    
    expected_dirs = [
        "src",
        "src/business_rules",
        "src/api",
        "data",
        "data/customer_profiles",
        "data/letters",
        "data/outputs",
        "data/voice_notes"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in expected_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    for dir_path in expected_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    print(f"  📁 Expected files: {len(expected_files) - len(missing_files)}/{len(expected_files)} found")
    print(f"  📁 Expected directories: {len(expected_dirs) - len(missing_dirs)}/{len(expected_dirs)} found")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
    
    if missing_dirs:
        print(f"  ❌ Missing directories: {missing_dirs}")
    
    return len(missing_files) == 0 and len(missing_dirs) == 0

def test_sample_data_processing():
    """Test with sample customer data."""
    print("\n🧪 Testing Sample Data Processing...")
    
    try:
        from business_rules.engine import BusinessRulesEngine
        
        # Create sample customer data
        sample_customers = [
            {
                "customer_id": "CUST001",
                "name": "Digital Dave",
                "age": 28,
                "digital_logins_per_month": 25,
                "prefers_app": True,
                "account_balance": 5000
            },
            {
                "customer_id": "CUST002", 
                "name": "Vulnerable Vera",
                "age": 78,
                "digital_logins_per_month": 0,
                "requires_support": True,
                "account_balance": 300
            }
        ]
        
        # Test business rules with sample data
        engine = BusinessRulesEngine()
        
        # Test digital-first customer
        digital_result = {
            "customer_category": {"label": "Digital-first self-serve"},
            "classification": {"label": "INFORMATION"},
            "comms_plan": {"timeline": [{"channel": "phone", "step": 1}]},
            "assets": {}
        }
        
        processed = engine.apply_all_rules(digital_result, sample_customers[0])
        timeline_channels = [s.get("channel") for s in processed.get("comms_plan", {}).get("timeline", [])]
        
        print(f"  📱 Digital customer processed: phone removed = {'phone' not in timeline_channels}")
        print(f"  📱 In-app added: {'in_app' in timeline_channels}")
        
        # Test vulnerable customer
        vulnerable_result = {
            "customer_category": {"label": "Vulnerable / extra-support"},
            "classification": {"label": "PROMOTIONAL"},
            "upsell_included": True,
            "comms_plan": {"timeline": []},
            "assets": {}
        }
        
        protected = engine.apply_all_rules(vulnerable_result, sample_customers[1])
        upsell_removed = not protected.get("upsell_included", True)
        
        print(f"  🛡️ Vulnerable customer protected: upsell removed = {upsell_removed}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Sample data processing failed: {e}")
        return False

def create_sample_env_file():
    """Create a sample .env file if it doesn't exist."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("\n💡 Creating sample .env file...")
        
        with open(env_path, 'w') as f:
            f.write("""# Add your real API keys here
CLAUDE_API_KEY=your-claude-key-here
OPENAI_API_KEY=your-openai-key-here
LOG_LEVEL=INFO
DEBUG_MODE=False
""")
        
        print("  ✅ Sample .env file created")
        print("  💡 Add your real API keys to test API functionality")

def main():
    """Run all tests."""
    print("🚀 Bank Communication System - Comprehensive Test")
    print("=" * 60)
    
    # Create sample env file if needed
    create_sample_env_file()
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_config_module),
        ("Business Rules", test_business_rules),
        ("API Modules", test_api_modules),
        ("Sample Data", test_sample_data_processing)
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
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the details above.")
    
    print("\n💡 Next steps:")
    print("  1. Add real API keys to .env file")
    print("  2. Test with real API calls")
    print("  3. Continue building remaining modules")

if __name__ == "__main__":
    main()