"""
Quick test to verify business rules are working
"""

import sys
import os
sys.path.append('src')

from business_rules.engine import BusinessRulesEngine
from business_rules.rules import rules_config

def test_rules_engine():
    """Test the business rules engine with sample data."""
    print("🧪 Testing Business Rules Engine...")
    print("=" * 50)
    
    # Create engine
    engine = BusinessRulesEngine()
    
    # Test 1: Vulnerable customer with promotional content
    print("\n📝 Test 1: Vulnerable Customer + Promotional Content")
    
    sample_result = {
        "customer_category": {"label": "Vulnerable / extra-support"},
        "classification": {"label": "PROMOTIONAL"},
        "upsell_included": True,
        "upsell_details": {"product": "Premium Account", "message": "Upgrade now!"},
        "assets": {
            "email_html": {"html": "<body>Promotional content here</body>"},
            "sms_text": "Special offer just for you!"
        },
        "comms_plan": {"timeline": []}
    }
    
    sample_profile = {"customer_id": "TEST123", "status": "vulnerable"}
    
    result = engine.apply_all_rules(sample_result, sample_profile)
    
    print(f"✅ Upsell removed: {not result.get('upsell_included', True)}")
    print(f"✅ Protection applied: {'VULNERABLE_PROTECTION' in str(result.get('comms_plan', {}))}")
    print(f"✅ Rules applied: {', '.join(engine.applied_rules)}")
    
    # Test 2: Digital-first customer
    print("\n📝 Test 2: Digital-First Customer")
    
    sample_result2 = {
        "customer_category": {"label": "Digital-first self-serve"},
        "classification": {"label": "INFORMATION"},
        "upsell_included": False,
        "assets": {},
        "comms_plan": {"timeline": [{"channel": "phone", "step": 1}]}
    }
    
    result2 = engine.apply_all_rules(sample_result2, {})
    timeline_channels = [step.get("channel") for step in result2.get("comms_plan", {}).get("timeline", [])]
    
    print(f"✅ Phone removed: {'phone' not in timeline_channels}")
    print(f"✅ In-app added: {'in_app' in timeline_channels}")
    print(f"✅ Voice note added: {'voice_note' in timeline_channels}")
    
    # Test 3: Regulatory communication
    print("\n📝 Test 3: Regulatory Communication")
    
    sample_result3 = {
        "customer_category": {"label": "Digital-first self-serve"},
        "classification": {"label": "REGULATORY"},
        "comms_plan": {"timeline": [{"channel": "email", "step": 1}]}
    }
    
    result3 = engine.apply_all_rules(sample_result3, {})
    timeline_channels3 = [step.get("channel") for step in result3.get("comms_plan", {}).get("timeline", [])]
    
    print(f"✅ Letter added: {'letter' in timeline_channels3}")
    print(f"✅ Regulatory override: {'REGULATORY_OVERRIDE' in str(result3.get('comms_plan', {}))}")
    
    print("\n🎉 All tests completed!")
    
    # Show rules summary
    print("\n📊 Active Rules Summary:")
    active_rules = engine.get_active_rules()
    for rule in active_rules:
        print(f"  ✅ {rule}")
    
    return True

if __name__ == "__main__":
    test_rules_engine()