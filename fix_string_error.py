"""
Fix the string literal error in customer_plans_ui.py
"""

from pathlib import Path

def fix_string_literals():
    """Fix unterminated string literal errors"""
    
    print("=" * 60)
    print("FIXING STRING LITERAL ERRORS")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/customer_plans_ui.py")
    
    if not file_path.exists():
        print(f"❌ Error: {file_path} not found!")
        return False
    
    print(f"📄 Reading {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"🔍 Finding and fixing line {84} area...")
    
    # Fix the specific problematic lines
    fixed_lines = []
    for i, line in enumerate(lines, 1):
        # Around line 84, fix the error message strings
        if i >= 80 and i <= 90:
            # Fix any broken string literals
            if 'st.error("❌ **Customer Analysis Required**' in line and not line.rstrip().endswith('")'):
                # This line is broken, fix it
                line = '                st.error("❌ **Customer Analysis Required** - Go to Customer Analysis and analyze your customer data first.")\n'
            elif 'st.error("❌ **Letters Required**' in line and not line.rstrip().endswith('")'):
                # Fix this one too
                line = '                st.error("❌ **Letters Required** - Go to Letter Management and upload/create letters first.")\n'
        
        fixed_lines.append(line)
    
    # Write back
    print("💾 Writing fixed content...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    # Now let's verify it compiles
    print("🧪 Testing compilation...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, str(file_path), 'exec')
        print("✅ File compiles successfully!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print("Applying comprehensive fix...")
        return comprehensive_fix(file_path)

def comprehensive_fix(file_path):
    """Completely rewrite the check_communication_prerequisites function"""
    
    print("\n🔨 Applying comprehensive fix...")
    
    # Read the entire file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the entire check_communication_prerequisites function
    new_function = '''
def check_communication_prerequisites():
    """Check if required data is available for communication planning."""
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None
    
    # Check for letters
    try:
        from file_handlers.letter_scanner import EnhancedLetterScanner
        scanner = EnhancedLetterScanner()
        letters = scanner.scan_all_letters()
        letters_available = len(letters) > 0
    except:
        letters_available = False
    
    if not customer_data_available or not letters_available:
        st.markdown("""
        <div style="background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="margin-top: 0; color: #92400E;">Prerequisites Required</h4>
            <p style="color: #92400E; margin-bottom: 0;">Complete the following before creating communication plans:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not customer_data_available:
                st.error("❌ Customer Analysis Required")
                st.markdown("Go to 'Customer Analysis' and analyze your customer data first.")
                
                # Add option to load test data
                st.markdown("---")
                st.markdown("**🧪 Or use test data for quick testing:**")
                
                if st.button("📊 Load 3 Test Customers", type="primary", use_container_width=True):
                    try:
                        import json
                        from pathlib import Path
                        test_file = Path("data/test_data/test_customers_analyzed.json")
                        if test_file.exists():
                            with open(test_file, 'r') as f:
                                st.session_state.analysis_results = json.load(f)
                            st.success("✅ Test dataset loaded successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Test dataset file not found. Run create_test_dataset.py first.")
                    except Exception as e:
                        st.error(f"Error loading test data: {e}")
                
                st.info("Test customers: Maria (Spanish), Vera (Vulnerable), Dave (Premium)")
                
            else:
                st.success("✅ Customer Data Ready")
                st.markdown("Customer analysis completed and available.")
                
                # Show option to switch to test data if wanted
                with st.expander("🧪 Switch to test data"):
                    if st.button("Load Test Dataset Instead", use_container_width=True):
                        try:
                            import json
                            from pathlib import Path
                            test_file = Path("data/test_data/test_customers_analyzed.json")
                            if test_file.exists():
                                with open(test_file, 'r') as f:
                                    st.session_state.analysis_results = json.load(f)
                                st.success("✅ Switched to test dataset!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        with col2:
            if not letters_available:
                st.error("❌ Letters Required")
                st.markdown("Go to 'Letter Management' and upload/create letters first.")
            else:
                st.success("✅ Letters Available")
                st.markdown(f"{len(letters)} letters ready for processing.")
        
        # Show currently loaded data info
        if customer_data_available:
            st.markdown("---")
            st.markdown("**📊 Current Data:**")
            if 'analysis_results' in st.session_state:
                customers = st.session_state.analysis_results.get('customer_categories', [])
                if len(customers) == 3:
                    # Likely test data
                    customer_names = [c.get('name', 'Unknown') for c in customers[:3]]
                    st.info(f"Test Data: {', '.join(customer_names)}")
                else:
                    st.info(f"Production Data: {len(customers)} customers")
        
        return False
    
    return True
'''
    
    # Find the function and replace it
    import re
    
    # Pattern to match the entire function
    pattern = r'def check_communication_prerequisites\(\):.*?(?=\ndef |\Z)'
    
    # Replace the function
    content = re.sub(pattern, new_function.strip() + '\n', content, flags=re.DOTALL)
    
    # Save the fixed content
    print("💾 Saving fixed function...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Test compilation again
    try:
        compile(content, str(file_path), 'exec')
        print("✅ Comprehensive fix successful!")
        return True
    except SyntaxError as e:
        print(f"❌ Still has error: {e}")
        return False

def verify_test_data_exists():
    """Make sure the test data file exists"""
    test_file = Path("data/test_data/test_customers_analyzed.json")
    
    if not test_file.exists():
        print("\n⚠️ Test data file doesn't exist. Creating it now...")
        
        # Create test data directory
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the test data directly here
        import json
        from datetime import datetime
        
        TEST_CUSTOMERS = {
            "customer_categories": [
                {
                    "customer_id": "CUST011",
                    "name": "Maria Garcia",
                    "age": 35,
                    "account_balance": 25000,
                    "digital_logins_per_month": 18,
                    "email": "maria.garcia@email.com",
                    "phone": "+44 7700 900123",
                    "preferred_language": "Spanish",
                    "category": "Digital-first self-serve",
                    "category_reasoning": [
                        "18 digital logins per month shows high engagement",
                        "Age 35 in prime digital demographic",
                        "£25,000 balance indicates established customer"
                    ],
                    "upsell_eligible": True,
                    "upsell_eligibility_reasoning": "Strong balance and engagement",
                    "upsell_products": ["Premium Account", "Travel Insurance"],
                    "financial_indicators": {
                        "account_health": "healthy",
                        "engagement_level": "high", 
                        "digital_maturity": "advanced"
                    },
                    "support_needs": [],
                    "preferred_channels": ["in_app", "email", "voice_note"],
                    "risk_factors": []
                },
                {
                    "customer_id": "CUST002",
                    "name": "Vulnerable Vera",
                    "age": 78,
                    "account_balance": 3500,
                    "digital_logins_per_month": 0,
                    "email": "vera.jones@email.com",
                    "phone": "+44 7700 900456",
                    "preferred_language": "English",
                    "category": "Vulnerable / extra-support",
                    "category_reasoning": [
                        "Age 78 requires extra care",
                        "No digital engagement",
                        "May need support with communications"
                    ],
                    "upsell_eligible": False,
                    "upsell_eligibility_reasoning": "Vulnerable customer - no sales",
                    "upsell_products": [],
                    "financial_indicators": {
                        "account_health": "vulnerable",
                        "engagement_level": "low",
                        "digital_maturity": "none"
                    },
                    "support_needs": ["Large print", "Phone support", "Extra time"],
                    "preferred_channels": ["letter", "phone"],
                    "risk_factors": ["Age", "No digital access", "Potential scam target"]
                },
                {
                    "customer_id": "CUST001", 
                    "name": "Digital Dave",
                    "age": 32,
                    "account_balance": 50000,
                    "digital_logins_per_month": 45,
                    "email": "dave.wilson@email.com",
                    "phone": "+44 7700 900789",
                    "preferred_language": "English",
                    "category": "Digital-first self-serve",
                    "category_reasoning": [
                        "45 logins per month - power user",
                        "Age 32 in core digital demographic",
                        "£50,000 balance - premium customer"
                    ],
                    "upsell_eligible": True,
                    "upsell_eligibility_reasoning": "Premium customer with high engagement",
                    "upsell_products": ["Wealth Management", "Premium Credit Card", "Investment ISA"],
                    "financial_indicators": {
                        "account_health": "excellent",
                        "engagement_level": "very_high",
                        "digital_maturity": "expert"
                    },
                    "support_needs": [],
                    "preferred_channels": ["in_app", "video_message", "email"],
                    "risk_factors": []
                }
            ],
            "aggregates": {
                "total_customers": 3,
                "categories": {
                    "Digital-first self-serve": 2,
                    "Vulnerable / extra-support": 1
                },
                "upsell_eligible_count": 2,
                "vulnerable_count": 1,
                "accessibility_needs_count": 1,
                "insights": [
                    "67% of customers are digital-first - prioritize app features",
                    "33% require vulnerable customer protection",
                    "67% eligible for upsell opportunities"
                ]
            },
            "segment_summaries": [
                {
                    "segment": "Digital-first self-serve",
                    "size": 2,
                    "description": "Comfortable with apps and email; quick to act",
                    "opportunities": ["In-app nudges", "Voice notes", "Video messages"]
                },
                {
                    "segment": "Vulnerable / extra-support",
                    "size": 1,
                    "description": "Needs softer tone and extra care",
                    "opportunities": ["Proactive callbacks", "No sales pressure"]
                }
            ],
            "analysis_metadata": {
                "total_analyzed": 3,
                "batch_size_used": 3,
                "api_model": "claude-3-5-sonnet-20241022",
                "analyzed_date": datetime.now().isoformat()
            }
        }
        
        # Save the test data
        with open(test_file, 'w') as f:
            json.dump(TEST_CUSTOMERS, f, indent=2, default=str)
        
        print("✅ Test dataset created successfully!")
    else:
        print("✅ Test data file exists")

if __name__ == "__main__":
    # First verify test data exists
    verify_test_data_exists()
    
    # Then fix the string literal errors
    success = fix_string_literals()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETE!")
        print("=" * 60)
        print("\nThe string literal errors have been fixed.")
        print("Test data loading is now optional with a button.")
        print("\nTry running:")
        print("  python -m streamlit run src/main.py")
    else:
        print("\n❌ Fix failed. Please check the errors above.")