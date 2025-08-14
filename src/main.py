"""
Resonance Bank - Complete Banking Interface
Modern banking interface with Customer Analysis, Cost Management, and Letter Processing.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config, is_configured
from api.api_manager import APIManager
from business_rules.engine import BusinessRulesEngine

# Import cost management modules
from communication_processing import (
    render_cost_configuration_ui, 
    render_cost_analyzer_ui,
    integrate_cost_analysis_with_api_manager
)

# Import file handlers module
from file_handlers.letter_scanner import render_enhanced_letter_management

# ============================================================================
# MODERN BANKING UI STYLING - (keeping the same as before)
# ============================================================================

def apply_modern_banking_styling():
    """Apply modern banking app styling."""
    st.markdown("""
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Modern banking color palette */
    :root {
        --primary-green: #00A86B;
        --secondary-green: #20B562;
        --light-green: #4CAF50;
        --gradient-green: linear-gradient(135deg, #00A86B 0%, #20B562 100%);
        --background-light: #F8F9FA;
        --background-white: #FFFFFF;
        --text-primary: #1A1A1A;
        --text-secondary: #6B7280;
        --text-light: #9CA3AF;
        --border-light: #E5E7EB;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
        --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }
    
    /* Global styling */
    .stApp {
        background: var(--background-light);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: var(--background-light);
        padding: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Modern header */
    .modern-header {
        background: var(--gradient-green);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 var(--radius-xl) var(--radius-xl);
        position: relative;
        overflow: hidden;
    }
    
    .modern-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: -50px;
        width: 200px;
        height: 200px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        transform: translate(50%, -50%);
    }
    
    .modern-header::after {
        content: '';
        position: absolute;
        bottom: -30px;
        left: -30px;
        width: 150px;
        height: 150px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
        text-align: center;
    }
    
    .bank-greeting {
        font-size: 1.1rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
        margin: 0 0 0.5rem 0;
    }
    
    .bank-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .bank-subtitle {
        font-size: 1rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.8);
        margin: 0.5rem 0 0 0;
    }
    
    /* Modern cards */
    .modern-card {
        background: var(--background-white);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .modern-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .modern-card.primary {
        background: var(--gradient-green);
        color: white;
        border: none;
    }
    
    .modern-card.primary .card-title,
    .modern-card.primary .card-subtitle,
    .modern-card.primary .metric-value {
        color: white;
    }
    
    /* Metric cards */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-green);
        margin: 0;
        line-height: 1.1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.25rem;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        display: inline-block;
    }
    
    .metric-delta.positive {
        color: #10B981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .metric-delta.negative {
        color: #EF4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .metric-delta.warning {
        color: #F59E0B;
        background: rgba(245, 158, 11, 0.1);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0.25rem;
    }
    
    .status-connected {
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: #EF4444;
    }
    
    /* Charts */
    .chart-container {
        background: var(--background-white);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        background: var(--primary-green);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--secondary-green);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .stSelectbox > div > div {
        background: var(--background-white);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--background-white);
        border-right: 1px solid var(--border-light);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: var(--text-primary);
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    p, div, span {
        color: var(--text-secondary);
    }
    </style>
    """, unsafe_allow_html=True)

def render_modern_header():
    """Render modern banking header."""
    st.markdown("""
    <div class="modern-header">
        <div class="header-content">
            <div class="bank-greeting">Good morning</div>
            <h1 class="bank-title">Resonance Bank</h1>
            <p class="bank-subtitle">Customer Communication Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DATA LOADING & PROCESSING - (keeping the same as before)
# ============================================================================

@st.cache_data
def load_customer_data():
    """Load customer data with caching."""
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None

# ============================================================================
# CUSTOMER ANALYSIS MODULE - (keeping the same as before but condensed)
# ============================================================================

def render_customer_analysis_page():
    """Complete Customer Analysis module."""
    st.markdown("""
    <div class="modern-card">
        <h2 style="margin-top: 0; color: #1A1A1A;">📊 Customer Analysis</h2>
        <p style="color: #6B7280;">Upload customer data and get AI-powered insights from Claude.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # File upload section
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">📁 Data Upload</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose your customer data file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file containing customer information"
    )
    
    # Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Use Sample Data", use_container_width=True):
            st.session_state.customer_data = load_sample_data()
            st.session_state.analysis_results = None
    
    with col2:
        if st.button("💡 View Data Template", use_container_width=True):
            show_data_template()
    
    with col3:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.customer_data = None
            st.session_state.analysis_results = None
    
    # Handle uploaded file
    if uploaded_file is not None:
        st.session_state.customer_data = process_uploaded_file(uploaded_file)
        st.session_state.analysis_results = None
    
    # Show analysis section if data is loaded
    if st.session_state.customer_data is not None:
        render_analysis_section(st.session_state.customer_data)
    
    # Show results if analysis was completed
    if st.session_state.analysis_results is not None:
        render_analysis_results(st.session_state.analysis_results)

def load_sample_data():
    """Load the sample customer data."""
    try:
        csv_path = Path("data/customer_profiles/sample_customers.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            st.success(f"✅ Loaded sample data: {len(df)} customers")
            return df
        else:
            st.error("Sample data not found. Please upload your own file.")
            return None
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        return None

def process_uploaded_file(uploaded_file):
    """Process the uploaded customer data file."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File uploaded successfully: {len(df)} customers, {len(df.columns)} fields")
        
        with st.expander("📋 Data Preview"):
            st.dataframe(df.head(), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Customers", len(df))
            with col2:
                st.metric("Data Fields", len(df.columns))
            with col3:
                numeric_cols = df.select_dtypes(include=['number']).columns
                st.metric("Numeric Fields", len(numeric_cols))
        
        return df
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def show_data_template():
    """Show the expected data template."""
    st.info("""
    **Expected Customer Data Fields:**
    
    **Required Fields:**
    - customer_id: Unique identifier
    - name: Customer name
    - age: Customer age
    - account_balance: Current balance
    
    **Recommended Fields:**
    - digital_logins_per_month: Digital engagement
    - mobile_app_usage: App usage level (high/medium/low)
    - email_opens_per_month: Email engagement
    - phone_calls_per_month: Phone support usage
    - branch_visits_per_month: Branch visit frequency
    - prefers_digital: Boolean preference
    - requires_support: Support needs
    - accessibility_needs: Special requirements
    """)

def render_analysis_section(customer_data):
    """Render the analysis configuration and execution."""
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">🤖 AI Analysis Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        batch_size = st.selectbox(
            "Batch Size",
            [5, 8, 10, 15],
            index=1,
            help="Number of customers to analyze per API call"
        )
    
    with col2:
        max_customers = st.selectbox(
            "Max Customers",
            ["All", "10", "25", "50"],
            index=0,
            help="Limit analysis for testing"
        )
    
    with col3:
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Standard", "Detailed", "Comprehensive"],
            index=1,
            help="Depth of AI analysis"
        )
    
    # Calculate customers to process
    if max_customers == "All":
        customers_to_process = len(customer_data)
    else:
        customers_to_process = min(int(max_customers), len(customer_data))
    
    # Analysis button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button(
            f"🚀 Analyze {customers_to_process} Customers",
            type="primary",
            use_container_width=True
        ):
            run_customer_analysis(customer_data.head(customers_to_process), batch_size)

def run_customer_analysis(customer_data, batch_size):
    """Run the AI customer analysis."""
    try:
        api_manager = APIManager()
    except Exception as e:
        st.error(f"Failed to initialize APIs: {str(e)}")
        return
    
    st.markdown("""
    <div class="modern-card primary">
        <h3 style="margin-top: 0; color: white;">🔄 AI Analysis in Progress</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            Claude is analyzing your customer data. This may take 30-60 seconds...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Prepare customer data
    customers_list = customer_data.to_dict('records')
    total_customers = len(customers_list)
    
    try:
        status_text.text(f"🤖 Sending {total_customers} customers to Claude for analysis...")
        progress_bar.progress(0.1)
        
        # Run the analysis
        analysis_results = api_manager.analyze_customer_base(
            customers_list, 
            batch_size=batch_size
        )
        
        progress_bar.progress(0.8)
        status_text.text("📊 Processing analysis results...")
        
        if analysis_results:
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")
            
            # Save results to session state
            st.session_state.analysis_results = analysis_results
            
            # Clear progress indicators after 2 seconds
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"🎉 Successfully analyzed {len(analysis_results.get('customer_categories', []))} customers!")
            st.rerun()
        else:
            progress_bar.empty()
            status_text.empty()
            st.error("❌ Analysis failed. Please check your API configuration and try again.")
            
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Analysis error: {str(e)}")

def render_analysis_results(analysis_results):
    """Render the comprehensive analysis results."""
    # Extract results
    customer_categories = analysis_results.get('customer_categories', [])
    aggregates = analysis_results.get('aggregates', {})
    
    # Results overview
    st.markdown("""
    <div class="modern-card primary">
        <h3 style="margin-top: 0; color: white;">📊 Analysis Results Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_analyzed = aggregates.get('total_customers', 0)
    upsell_eligible = aggregates.get('upsell_eligible_count', 0)
    vulnerable_count = aggregates.get('vulnerable_count', 0)
    accessibility_count = aggregates.get('accessibility_needs_count', 0)
    
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{total_analyzed}</div>
            <div class="metric-label">CUSTOMERS ANALYZED</div>
            <div class="metric-delta positive">100% processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        upsell_pct = (upsell_eligible / total_analyzed * 100) if total_analyzed > 0 else 0
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{upsell_eligible}</div>
            <div class="metric-label">UPSELL ELIGIBLE</div>
            <div class="metric-delta positive">{upsell_pct:.0f}% of base</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{vulnerable_count}</div>
            <div class="metric-label">VULNERABLE CUSTOMERS</div>
            <div class="metric-delta warning">Need protection</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{accessibility_count}</div>
            <div class="metric-label">ACCESSIBILITY NEEDS</div>
            <div class="metric-delta warning">Special requirements</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Customer insights
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">💡 Key Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    insights = aggregates.get('insights', [])
    
    for i, insight in enumerate(insights):
        st.markdown(f"""
        <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #00A86B;">
            <strong>Insight {i+1}:</strong> {insight}
        </div>
        """, unsafe_allow_html=True)
    
    # Individual customer details
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">👥 Individual Customer Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create summary dataframe
    customer_summary = []
    
    for customer in customer_categories:
        customer_summary.append({
            'Customer ID': customer.get('customer_id', 'Unknown'),
            'Name': customer.get('name', 'Unknown'),
            'Category': customer.get('category', 'Unknown'),
            'Upsell Eligible': '✅' if customer.get('upsell_eligible') else '❌',
            'Account Health': customer.get('financial_indicators', {}).get('account_health', 'Unknown'),
            'Digital Maturity': customer.get('financial_indicators', {}).get('digital_maturity', 'Unknown')
        })
    
    if customer_summary:
        df = pd.DataFrame(customer_summary)
        st.dataframe(df, use_container_width=True, height=400)
    
    # Download section
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">📥 Download Results</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = pd.DataFrame(customer_summary).to_csv(index=False)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"customer_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = json.dumps(analysis_results, indent=2, default=str)
        st.download_button(
            label="🔄 Download JSON",
            data=json_data,
            file_name=f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def render_system_status():
    """Render system status."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">System Status</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Check configuration
    config_status = "connected" if is_configured() else "error"
    config_label = "SYSTEM READY" if is_configured() else "CONFIG NEEDED"
    
    with col1:
        st.markdown(f'<span class="status-indicator status-{config_status}">{config_label}</span>', unsafe_allow_html=True)
    
    # Check API status
    try:
        api_manager = APIManager()
        status = api_manager.get_api_status()
        claude_status = "connected" if status.get('claude', {}).get('status') == 'connected' else "error"
        openai_status = "connected" if status.get('openai', {}).get('status') == 'connected' else "error"
    except:
        claude_status = openai_status = "error"
    
    with col2:
        st.markdown(f'<span class="status-indicator status-{claude_status}">CLAUDE AI</span>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<span class="status-indicator status-{openai_status}">OPENAI</span>', unsafe_allow_html=True)
    
    # Check data
    customer_data = load_customer_data()
    data_status = "connected" if customer_data is not None else "warning"
    data_label = "DATA LOADED" if data_status == "connected" else "NO DATA"
    
    with col4:
        st.markdown(f'<span class="status-indicator status-{data_status}">{data_label}</span>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard_overview():
    """Render dashboard overview."""
    customer_data = load_customer_data()
    
    if customer_data is None:
        st.warning("Customer data not available.")
        return
    
    # Calculate totals
    total_customers = len(customer_data)
    total_balance = customer_data['account_balance'].sum()
    avg_balance = customer_data['account_balance'].mean()
    digital_users = len(customer_data[customer_data['prefers_digital'] == True])
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{total_customers}</div>
            <div class="metric-label">TOTAL CUSTOMERS</div>
            <div class="metric-delta positive">+2.4% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{avg_balance:,.0f}</div>
            <div class="metric-label">AVERAGE BALANCE</div>
            <div class="metric-delta positive">+5.1% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{digital_users}</div>
            <div class="metric-label">DIGITAL USERS</div>
            <div class="metric-delta positive">{(digital_users/total_customers)*100:.0f}% adoption</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        high_value = len(customer_data[customer_data['account_balance'] > 10000])
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{high_value}</div>
            <div class="metric-label">HIGH VALUE</div>
            <div class="metric-delta positive">Premium segment</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application with navigation."""
    st.set_page_config(
        page_title="Resonance Bank - Communication Intelligence",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_modern_banking_styling()
    render_modern_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.selectbox(
            "Select Module",
            ["Executive Dashboard", "Customer Analysis", "Letter Management", "Cost Management", "Communication Processing", "System Monitor"],
            index=0
        )
    
    # Main content routing
    if page == "Executive Dashboard":
        render_system_status()
        render_dashboard_overview()
    
    elif page == "Customer Analysis":
        render_customer_analysis_page()
    
    elif page == "Letter Management":
        from file_handlers.letter_scanner import render_enhanced_letter_management
        render_enhanced_letter_management()
    
    elif page == "Cost Management":
        st.markdown("## 💰 Cost Management")
        
        tab1, tab2 = st.tabs(["Configuration", "Analysis"])
        
        with tab1:
            render_cost_configuration_ui()
        
        with tab2:
            # Get customer data from session state if available
            customer_categories = st.session_state.get("analysis_results", {}).get("customer_categories", [])
            render_cost_analyzer_ui(customer_categories)
    
    elif page == "Communication Processing":
        st.markdown("## 💬 Communication Processing Module")
        st.info("Individual customer communication processing coming next...")
    
    elif page == "System Monitor":
        st.markdown("## 📊 System Performance Monitor")
        st.info("System monitoring functionality coming next...")

if __name__ == "__main__":
    main()