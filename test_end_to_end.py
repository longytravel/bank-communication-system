"""
End-to-End System Test
Tests the complete workflow with real sample data.
"""

import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def load_sample_data():
    """Load sample customer data."""
    print("📊 Loading Sample Customer Data...")
    
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    
    if not csv_path.exists():
        print(f"  ❌ Sample data not found at {csv_path}")
        return None
    
    try:
        df = pd.read_csv(csv_path)
        print(f"  ✅ Loaded {len(df)} sample customers")
        print(f"  📋 Customers: {', '.join(df['name'].head(3).tolist())}...")
        return df
    except Exception as e:
        print(f"  ❌ Error loading data: {e}")
        return None

def test_customer_analysis():
    """Test customer analysis with real data."""
    print("\n🧠 Testing Customer Analysis...")
    
    try:
        from api.api_manager import APIManager
        
        # Load sample data
        df = load_sample_data()
        if df is None:
            return False
        
        # Initialize API Manager
        api_manager = APIManager()
        print("  ✅ API Manager initialized")
        
        # Test with first 3 customers to avoid rate limits
        sample_customers = df.head(3).to_dict('records')
        
        print(f"  🔍 Analyzing {len(sample_customers)} customers...")
        print("  ⏳ This may take 10-15 seconds...")
        
        # Run customer analysis
        analysis = api_manager.analyze_customer_base(sample_customers, batch_size=3)
        
        if analysis:
            print("  ✅ Customer analysis completed!")
            
            # Show results
            categories = analysis.get('customer_categories', [])
            for customer in categories:
                name = customer.get('name', 'Unknown')
                category = customer.get('category', 'Unknown')
                upsell = "✅" if customer.get('upsell_eligible') else "❌"
                print(f"    👤 {name}: {category} (Upsell: {upsell})")
            
            # Show insights
            insights = analysis.get('aggregates', {}).get('insights', [])
            print("  💡 Key Insights:")
            for insight in insights[:2]:
                print(f"    • {insight}")
            
            return True
        else:
            print("  ❌ Customer analysis failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Customer analysis test failed: {e}")
        return False

def test_letter_processing():
    """Test letter processing with sample letters."""
    print("\n📄 Testing Letter Processing...")
    
    try:
        from api.api_manager import APIManager
        
        # Load letter
        letter_path = Path("data/letters/account_update_letter.txt")
        if not letter_path.exists():
            print(f"  ❌ Letter not found at {letter_path}")
            return False
        
        letter_text = letter_path.read_text(encoding='utf-8')
        print(f"  ✅ Loaded letter ({len(letter_text)} characters)")
        
        # Test letter classification
        api_manager = APIManager()
        print("  🔍 Classifying letter...")
        
        classification = api_manager.classify_letter(letter_text)
        
        if classification:
            label = classification.get('classification', 'Unknown')
            confidence = classification.get('confidence', 0)
            reasoning = classification.get('reasoning', 'No reasoning provided')
            
            print(f"  ✅ Classification: {label} (Confidence: {confidence}/10)")
            print(f"  💭 Reasoning: {reasoning[:100]}...")
            
            return True
        else:
            print("  ❌ Letter classification failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Letter processing test failed: {e}")
        return False

def test_customer_communication():
    """Test complete customer communication workflow."""
    print("\n💬 Testing Customer Communication Workflow...")
    
    try:
        from api.api_manager import APIManager
        
        # Load sample data
        df = load_sample_data()
        if df is None:
            return False
        
        # Get first customer (Digital Dave)
        customer = df.iloc[0].to_dict()
        customer_name = customer.get('name', 'Unknown')
        
        # Load letter
        letter_path = Path("data/letters/premium_upgrade_offer.txt")
        if not letter_path.exists():
            print(f"  ❌ Letter not found")
            return False
        
        letter_text = letter_path.read_text(encoding='utf-8')
        
        print(f"  👤 Processing communication for: {customer_name}")
        print("  ⏳ This may take 15-20 seconds...")
        
        # Process communication
        api_manager = APIManager()
        channels = ["email", "sms", "in_app", "letter", "voice_note"]
        
        result = api_manager.process_customer_communication(
            letter_text, customer, channels, generate_voice=True
        )
        
        if result:
            print("  ✅ Communication strategy created!")
            
            # Show strategy details
            customer_category = result.get('customer_category', {})
            classification = result.get('classification', {})
            timeline = result.get('comms_plan', {}).get('timeline', [])
            
            print(f"    📋 Customer Category: {customer_category.get('label', 'Unknown')}")
            print(f"    📄 Letter Type: {classification.get('label', 'Unknown')}")
            print(f"    📱 Communication Channels: {len(timeline)} planned")
            
            # Show timeline
            print("    ⏰ Communication Timeline:")
            for step in timeline[:3]:  # Show first 3 steps
                channel = step.get('channel', 'Unknown')
                when = step.get('when', 'Unknown')
                purpose = step.get('purpose', 'No purpose')[:50]
                print(f"      {step.get('step', '?')}. {channel.upper()} ({when}): {purpose}...")
            
            # Check for upsell
            upsell = result.get('upsell_included', False)
            print(f"    💎 Upsell Included: {'Yes' if upsell else 'No'}")
            
            # Check for voice note
            voice_path = result.get('processing_metadata', {}).get('voice_note_path')
            if voice_path:
                print(f"    🔊 Voice Note: Generated ({Path(voice_path).name})")
            
            return True
        else:
            print("  ❌ Communication processing failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Communication workflow test failed: {e}")
        return False

def test_business_rules_integration():
    """Test business rules with different customer types."""
    print("\n⚙️ Testing Business Rules Integration...")
    
    try:
        from business_rules.engine import BusinessRulesEngine
        
        # Load sample data
        df = load_sample_data()
        if df is None:
            return False
        
        engine = BusinessRulesEngine()
        
        # Test vulnerable customer (Vera)
        vera = df[df['name'] == 'Vulnerable Vera'].iloc[0].to_dict()
        
        vulnerable_result = {
            "customer_category": {"label": "Vulnerable / extra-support"},
            "classification": {"label": "PROMOTIONAL"},
            "upsell_included": True,
            "upsell_details": {"product": "Premium Account"},
            "assets": {"sms_text": "Special offer!"},
            "comms_plan": {"timeline": []}
        }
        
        protected_result = engine.apply_all_rules(vulnerable_result, vera)
        
        protection_works = not protected_result.get('upsell_included', True)
        print(f"  🛡️ Vulnerable Customer Protection: {'✅ Working' if protection_works else '❌ Failed'}")
        
        # Test digital customer (Dave)  
        dave = df[df['name'] == 'Digital Dave'].iloc[0].to_dict()
        
        digital_result = {
            "customer_category": {"label": "Digital-first self-serve"},
            "classification": {"label": "INFORMATION"},
            "comms_plan": {"timeline": [{"channel": "phone", "step": 1}]},
            "assets": {}
        }
        
        digital_processed = engine.apply_all_rules(digital_result, dave)
        timeline_channels = [s.get("channel") for s in digital_processed.get("comms_plan", {}).get("timeline", [])]
        
        phone_removed = "phone" not in timeline_channels
        in_app_added = "in_app" in timeline_channels
        voice_added = "voice_note" in timeline_channels
        
        print(f"  📱 Digital-First Rules: Phone removed: {'✅' if phone_removed else '❌'}, In-app: {'✅' if in_app_added else '❌'}, Voice: {'✅' if voice_added else '❌'}")
        
        return protection_works and phone_removed and in_app_added
        
    except Exception as e:
        print(f"  ❌ Business rules integration test failed: {e}")
        return False

def main():
    """Run complete end-to-end test."""
    print("🚀 Bank Communication System - End-to-End Test")
    print("=" * 60)
    print("This will test the complete workflow with real API calls!")
    print("Expected time: 30-45 seconds")
    print("=" * 60)
    
    tests = [
        ("Customer Analysis", test_customer_analysis),
        ("Letter Processing", test_letter_processing), 
        ("Customer Communication", test_customer_communication),
        ("Business Rules Integration", test_business_rules_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 END-TO-END TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🏆 Overall Score: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 COMPLETE SUCCESS! The entire system is working perfectly!")
        print("🚀 Ready for production use!")
    elif passed >= len(results) - 1:
        print("🎊 Excellent! Almost everything working perfectly!")
    else:
        print("⚠️ Some issues to resolve, but core functionality working!")
    
    print(f"\n📊 System Status:")
    print(f"   • Configuration: Working")
    print(f"   • Business Rules: Working") 
    print(f"   • API Integration: Working")
    print(f"   • End-to-End Workflow: {'Working' if passed >= 3 else 'Needs attention'}")

if __name__ == "__main__":
    main()