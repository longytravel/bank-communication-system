"""
Add test data loader to Customer Communication Plans
This lets you skip customer analysis and use test data instantly
"""

from pathlib import Path

def add_test_loader_to_ui():
    """Add test data loader to the UI."""
    
    print("Adding test data loader to UI...")
    
    # File to update
    ui_file = Path("src/communication_processing/customer_plans_ui.py")
    
    # Read the file
    content = ui_file.read_text(encoding='utf-8')
    
    # Find the check_communication_prerequisites function
    # We need to add a test data loader there
    
    # Add this code right after the prerequisites check
    test_loader_code = '''
    # TEST DATA LOADER - Skip analysis requirement
    if not customer_data_available:
        st.markdown("""
        ### 🚀 Quick Test Mode Available
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Load Test Dataset (3 Customers)", type="primary", use_container_width=True):
                # Load the test dataset
                try:
                    import json
                    test_file = Path("data/test_data/test_customers_analyzed.json")
                    
                    if test_file.exists():
                        with open(test_file, 'r') as f:
                            test_data = json.load(f)
                        
                        # Put it in session state
                        st.session_state.analysis_results = test_data
                        st.success("✅ Test data loaded! 3 customers ready.")
                        st.rerun()
                    else:
                        st.error("Test dataset not found. Run create_test_dataset.py first.")
                except Exception as e:
                    st.error(f"Error loading test data: {e}")
        
        with col2:
            st.info("This loads Maria (Spanish), Vera (Vulnerable), and Dave (Premium)")
        
        st.markdown("---")
        st.markdown("**Or analyze real customers:**")
    '''
    
    # Find where to insert it
    marker = "# Check for customer analysis results"
    if marker in content:
        # Add our code after the marker
        parts = content.split(marker)
        content = parts[0] + marker + test_loader_code + parts[1]
    else:
        # Try different approach - add after check_communication_prerequisites function starts
        marker2 = "customer_data_available = 'analysis_results' in st.session_state"
        if marker2 in content:
            # Add imports at the top if not there
            if "from pathlib import Path" not in content:
                content = "from pathlib import Path\n" + content
            if "import json" not in content:
                content = "import json\n" + content
    
    # Save the updated file
    ui_file.write_text(content, encoding='utf-8')
    print("✅ Test loader added to UI!")
    
    return True

def create_simple_fix():
    """Simpler approach - modify the check itself."""
    
    print("\n🔧 Alternative fix - modifying prerequisites check...")
    
    ui_file = Path("src/communication_processing/customer_plans_ui.py")
    content = ui_file.read_text(encoding='utf-8')
    
    # Replace the prerequisites check
    old_check = """def check_communication_prerequisites():
    \"\"\"Check if required data is available for communication planning.\"\"\"
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None"""
    
    new_check = """def check_communication_prerequisites():
    \"\"\"Check if required data is available for communication planning.\"\"\"
    
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
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None"""
    
    if "def check_communication_prerequisites():" in content:
        content = content.replace(old_check, new_check)
        ui_file.write_text(content, encoding='utf-8')
        print("✅ Auto-loader added!")
        return True
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING TEST DATA LOADER")
    print("=" * 60)
    
    # Try the simple fix
    success = create_simple_fix()
    
    if success:
        print("\n✅ SUCCESS! Test data will now auto-load!")
        print("\n📱 To use:")
        print("1. Refresh your browser (or restart streamlit)")
        print("2. Go to Customer Communication Plans")
        print("3. Test data will load automatically!")
        print("4. You can now generate plans immediately!")
    else:
        print("\n❌ Manual fix needed")