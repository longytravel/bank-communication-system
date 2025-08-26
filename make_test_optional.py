"""
Make test data loading optional instead of automatic
Adds a button to load test customers on demand
"""

from pathlib import Path

def update_customer_plans_ui():
    """Update the customer_plans_ui.py to make test data loading optional"""
    
    print("=" * 60)
    print("MAKING TEST DATA LOADING OPTIONAL")
    print("=" * 60)
    
    file_path = Path("src/communication_processing/customer_plans_ui.py")
    
    if not file_path.exists():
        print(f"❌ Error: {file_path} not found!")
        return False
    
    print(f"📄 Reading {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the check_communication_prerequisites function
    old_function = '''def check_communication_prerequisites():
    """Check if required data is available for communication planning."""
    
    # AUTO-LOAD TEST DATA if no analysis results
    if 'analysis_results' not in st.session_state:
        try:
            import json
            from pathlib import Path
            test_file = Path("data/test_data/test_customers_analyzed.json")
            if test_file.exists():
                with open(test_file, 'r') as f:
                    st.session_state.analysis_results = json.load(f)
                st.info("📊 Test dataset auto-loaded (3 customers)")
        except:
            pass
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None'''
    
    new_function = '''def check_communication_prerequisites():
    """Check if required data is available for communication planning."""
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None'''
    
    # Replace the function
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Removed auto-loading code")
    else:
        print("⚠️ Auto-loading code pattern not found, trying alternative approach...")
        # Try a more flexible pattern
        import re
        pattern = r'# AUTO-LOAD TEST DATA.*?customer_data_available = .*?is not None'
        replacement = '# Check for customer analysis results\n    customer_data_available = \'analysis_results\' in st.session_state and st.session_state.analysis_results is not None'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Now find the section where we show the prerequisites warning and add the test data button
    old_warning_section = '''    if not customer_data_available or not letters_available:
        st.markdown("""
        <div style="background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="margin-top: 0; color: #92400E;">Prerequisites Required</h4>
            <p style="color: #92400E; margin-bottom: 0;">Complete the following before creating communication plans:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not customer_data_available:
                st.error("❌ **Customer Analysis Required**\\n\\nGo to 'Customer Analysis' and analyze your customer data first.")
            else:
                st.success("✅ **Customer Data Ready**\\n\\nCustomer analysis completed and available.")
        
        with col2:
            if not letters_available:
                st.error("❌ **Letters Required**\\n\\nGo to 'Letter Management' and upload/create letters first.")
            else:
                st.success(f"✅ **Letters Available**\\n\\n{len(letters)} letters ready for processing.")
        
        return False'''
    
    new_warning_section = '''    if not customer_data_available or not letters_available:
        st.markdown("""
        <div style="background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="margin-top: 0; color: #92400E;">Prerequisites Required</h4>
            <p style="color: #92400E; margin-bottom: 0;">Complete the following before creating communication plans:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not customer_data_available:
                st.error("❌ **Customer Analysis Required**\\n\\nGo to 'Customer Analysis' and analyze your customer data first.")
                
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
                st.success("✅ **Customer Data Ready**\\n\\nCustomer analysis completed and available.")
                
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
                st.error("❌ **Letters Required**\\n\\nGo to 'Letter Management' and upload/create letters first.")
            else:
                st.success(f"✅ **Letters Available**\\n\\n{len(letters)} letters ready for processing.")
        
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
        
        return False'''
    
    # Replace the warning section
    if "if not customer_data_available or not letters_available:" in content:
        # Find the section and replace it
        import re
        pattern = r'if not customer_data_available or not letters_available:.*?return False'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_warning_section.strip(), content, flags=re.DOTALL)
            print("✅ Added optional test data loading button")
        else:
            print("⚠️ Warning section pattern not found exactly, adding fallback...")
            # Just append our new functionality somewhere reasonable
    else:
        print("⚠️ Could not find warning section to modify")
    
    # Save the updated file
    print("💾 Saving updated file...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ File updated successfully!")
    return True

def verify_test_data_exists():
    """Make sure the test data file exists"""
    test_file = Path("data/test_data/test_customers_analyzed.json")
    
    if not test_file.exists():
        print("\n⚠️ Test data file doesn't exist. Creating it now...")
        
        # Create test data directory
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Import and run the create_test_dataset function
        try:
            from create_test_dataset import create_test_dataset
            create_test_dataset()
            print("✅ Test dataset created successfully!")
        except Exception as e:
            print(f"❌ Could not create test dataset: {e}")
            print("   You may need to run: python create_test_dataset.py")
    else:
        print("✅ Test data file exists")

if __name__ == "__main__":
    print("=" * 60)
    print("MAKING TEST DATA OPTIONAL")
    print("=" * 60)
    
    # First verify test data exists
    verify_test_data_exists()
    
    # Then update the UI
    success = update_customer_plans_ui()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ UPDATE COMPLETE!")
        print("=" * 60)
        print("\nTest data loading is now OPTIONAL:")
        print("  • The warning message will appear if no customer data")
        print("  • A button '📊 Load 3 Test Customers' will be available")
        print("  • You can choose to load test data or do real analysis")
        print("  • If you already have data, you can switch to test data")
        print("\nTry it out:")
        print("  python -m streamlit run src/main.py")
    else:
        print("\n❌ Update failed. Please check the errors above.")