"""
Resonance Bank - Professional Banking Communication Platform
Enterprise-grade banking interface with AI-powered communication intelligence.
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

# Import the new professional theme
from ui.professional_theme import (
    apply_professional_theme,
    render_professional_header,
    create_metric_card,
    create_status_badge,
    create_professional_card
)

# Import cost management modules
from communication_processing import (
    render_cost_configuration_ui, 
    render_cost_analyzer_ui,
    integrate_cost_analysis_with_api_manager
)

# Import batch processing (lazy import to avoid circular dependency)
def get_batch_processing_ui():
    from communication_processing.batch_ui import render_batch_communication_processing
    return render_batch_communication_processing

# Import file handlers module
from file_handlers.letter_scanner import render_enhanced_letter_management

# ============================================================================
# PROFESSIONAL COMPONENTS
# ============================================================================

def render_navigation_sidebar():
    """Render professional navigation sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="font-size: 0.875rem; font-weight: 600; text-transform: uppercase; 
                       letter-spacing: 0.05em; color: #64748B; margin-bottom: 1rem;">
                Navigation
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation options with descriptions
        nav_options = {
            "Executive Dashboard": "System overview and key metrics",
            "Customer Analysis": "AI-powered customer segmentation",
            "Letter Management": "Document classification and management",
            "Batch Processing": "Multi-customer communication workflows",
            "Cost Management": "Communication cost optimization",
            "System Configuration": "Settings and API configuration"
        }
        
        selected_page = st.selectbox(
            "Select Module",
            options=list(nav_options.keys()),
            format_func=lambda x: x,
            help="Choose a module to navigate to"
        )
        
        # Show module description
        st.markdown(f"""
        <div style="padding: 0.5rem; background: #F8FAFC; border-radius: 6px; margin-top: 0.5rem;">
            <p style="font-size: 0.75rem; color: #64748B; margin: 0;">
                {nav_options[selected_page]}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # System status in sidebar
        st.markdown("""
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #E2E8F0;">
            <h3 style="font-size: 0.875rem; font-weight: 600; text-transform: uppercase; 
                       letter-spacing: 0.05em; color: #64748B; margin-bottom: 0.5rem;">
                System Status
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        render_sidebar_status()
        
    return selected_page

def render_sidebar_status():
    """Render system status in sidebar."""
    try:
        api_manager = APIManager()
        status = api_manager.get_api_status()
        claude_connected = status.get('claude', {}).get('status') == 'connected'
        openai_connected = status.get('openai', {}).get('status') == 'connected'
    except:
        claude_connected = False
        openai_connected = False
    
    status_items = [
        ("Configuration", is_configured(), "active" if is_configured() else "error"),
        ("Claude AI", claude_connected, "active" if claude_connected else "error"),
        ("OpenAI", openai_connected, "active" if openai_connected else "error"),
    ]
    
    for label, connected, status in status_items:
        badge = create_status_badge("Connected" if connected else "Disconnected", status)
        st.markdown(f"""
        <div style="margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.875rem; color: #0F172A;">{label}</span>
            {badge}
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def render_executive_dashboard():
    """Render the executive dashboard with professional metrics."""
    
    # Page header
    st.markdown("""
    <div class="pro-card">
        <h1 style="font-size: 1.875rem; font-weight: 700; color: #0F172A; margin: 0;">
            Executive Dashboard
        </h1>
        <p style="color: #64748B; margin-top: 0.5rem;">
            Real-time overview of communication system performance and metrics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    customer_data = load_customer_data()
    
    if customer_data is not None:
        # Calculate metrics
        total_customers = len(customer_data)
        avg_balance = customer_data['account_balance'].mean()
        digital_users = len(customer_data[customer_data['prefers_digital'] == True])
        digital_rate = (digital_users/total_customers)*100 if total_customers > 0 else 0
        high_value = len(customer_data[customer_data['account_balance'] > 10000])
        
        # Key Performance Indicators
        st.markdown("""
        <h2 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
            Key Performance Indicators
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card(
                "Total Customers",
                f"{total_customers:,}",
                "+2.4% vs last month",
                "positive"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card(
                "Average Balance",
                f"£{avg_balance:,.0f}",
                "+5.1% vs last month",
                "positive"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card(
                "Digital Adoption",
                f"{digital_rate:.1f}%",
                f"{digital_users:,} users",
                "positive"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card(
                "High Value Accounts",
                f"{high_value:,}",
                "Premium segment",
                "neutral"
            ), unsafe_allow_html=True)
        
        # Charts Section
        render_dashboard_charts(customer_data)
        
        # Recent Activity
        render_recent_activity()
    else:
        st.warning("No customer data available. Please upload data in the Customer Analysis module.")

def render_dashboard_charts(customer_data):
    """Render professional charts for the dashboard."""
    st.markdown("""
    <h2 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin: 2rem 0 1rem 0;">
        Analytics Overview
    </h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Digital vs Non-Digital Distribution
        digital_counts = customer_data['prefers_digital'].value_counts()
        fig_digital = go.Figure(data=[go.Pie(
            labels=['Digital' if x else 'Traditional' for x in digital_counts.index],
            values=digital_counts.values,
            hole=0.4,
            marker_colors=['#3B82F6', '#E2E8F0']
        )])
        fig_digital.update_layout(
            title="Channel Preference Distribution",
            font=dict(family="IBM Plex Sans"),
            height=300,
            showlegend=True,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_digital, use_container_width=True)
    
    with col2:
        # Balance Distribution
        fig_balance = px.histogram(
            customer_data,
            x='account_balance',
            nbins=20,
            title="Account Balance Distribution"
        )
        fig_balance.update_traces(marker_color='#3B82F6')
        fig_balance.update_layout(
            font=dict(family="IBM Plex Sans"),
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis_title="Balance (£)",
            yaxis_title="Customer Count"
        )
        st.plotly_chart(fig_balance, use_container_width=True)

def render_recent_activity():
    """Render recent activity section."""
    st.markdown("""
    <h2 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin: 2rem 0 1rem 0;">
        Recent System Activity
    </h2>
    """, unsafe_allow_html=True)
    
    # Mock recent activities
    activities = [
        {"time": "2 minutes ago", "action": "Customer batch analyzed", "details": "25 customers processed", "status": "success"},
        {"time": "15 minutes ago", "action": "Letter classified", "details": "Regulatory communication", "status": "success"},
        {"time": "1 hour ago", "action": "Cost analysis completed", "details": "£12,450 saved", "status": "success"},
        {"time": "2 hours ago", "action": "API connection test", "details": "All systems operational", "status": "success"},
    ]
    
    for activity in activities:
        status_color = "#10B981" if activity["status"] == "success" else "#EF4444"
        st.markdown(f"""
        <div style="padding: 0.75rem; border-left: 3px solid {status_color}; 
                    background: #F8FAFC; margin-bottom: 0.5rem; border-radius: 0 6px 6px 0;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 500; color: #0F172A; font-size: 0.875rem;">{activity['action']}</div>
                    <div style="color: #64748B; font-size: 0.75rem; margin-top: 0.25rem;">{activity['details']}</div>
                </div>
                <div style="color: #94A3B8; font-size: 0.75rem;">{activity['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# CUSTOMER ANALYSIS PAGE (Professional Version)
# ============================================================================

def render_customer_analysis_page():
    """Render professional customer analysis page."""
    
    st.markdown(create_professional_card(
        "Customer Analysis",
        "AI-powered customer segmentation and insights"
    ), unsafe_allow_html=True)
    
    # Initialize session state
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Data Upload", "Analysis Configuration", "Results"])
    
    with tab1:
        render_data_upload_tab()
    
    with tab2:
        render_analysis_configuration_tab()
    
    with tab3:
        render_analysis_results_tab()

def render_data_upload_tab():
    """Render the data upload tab."""
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Upload Customer Data
    </h3>
    <p style="color: #64748B; font-size: 0.875rem; margin-bottom: 1.5rem;">
        Upload a CSV or Excel file containing customer information for AI analysis.
    </p>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose file",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, Excel"
    )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Use Sample Data", use_container_width=True):
            st.session_state.customer_data = load_sample_data()
            st.session_state.analysis_results = None
            st.success("Sample data loaded successfully")
    
    with col2:
        if st.button("View Template", use_container_width=True):
            show_data_template()
    
    with col3:
        if st.button("Clear Data", use_container_width=True, type="secondary"):
            st.session_state.customer_data = None
            st.session_state.analysis_results = None
            st.info("Data cleared")
    
    # Handle uploaded file
    if uploaded_file is not None:
        st.session_state.customer_data = process_uploaded_file(uploaded_file)
        st.session_state.analysis_results = None
    
    # Show data preview if loaded
    if st.session_state.customer_data is not None:
        df = st.session_state.customer_data
        st.markdown(f"""
        <div style="margin-top: 1.5rem; padding: 1rem; background: #F8FAFC; border-radius: 6px;">
            <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
                Data Summary
            </h4>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{len(df):,}</div>
                    <div style="font-size: 0.75rem; color: #64748B;">Total Records</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{len(df.columns)}</div>
                    <div style="font-size: 0.75rem; color: #64748B;">Data Fields</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">
                        {len(df.select_dtypes(include=['number']).columns)}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748B;">Numeric Fields</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Data Sample"):
            st.dataframe(df.head(10), use_container_width=True)

def render_analysis_configuration_tab():
    """Render analysis configuration tab."""
    if st.session_state.customer_data is None:
        st.info("Please upload customer data first.")
        return
    
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Configure AI Analysis
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        batch_size = st.selectbox(
            "Batch Size",
            [5, 8, 10, 15],
            index=1,
            help="Number of customers per API call"
        )
    
    with col2:
        max_customers = st.selectbox(
            "Maximum Customers",
            ["All", "10", "25", "50", "100"],
            index=0,
            help="Limit for testing purposes"
        )
    
    with col3:
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Standard", "Detailed", "Comprehensive"],
            index=1,
            help="Level of analysis detail"
        )
    
    # Calculate customers to process
    customer_data = st.session_state.customer_data
    if max_customers == "All":
        customers_to_process = len(customer_data)
    else:
        customers_to_process = min(int(max_customers), len(customer_data))
    
    # Analysis summary
    st.markdown(f"""
    <div style="margin: 1.5rem 0; padding: 1rem; background: #F8FAFC; border-radius: 6px;">
        <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Analysis Summary
        </h4>
        <ul style="margin: 0; padding-left: 1.5rem; color: #64748B; font-size: 0.875rem;">
            <li>Customers to analyze: <strong>{customers_to_process:,}</strong></li>
            <li>Estimated time: <strong>{customers_to_process * 2} seconds</strong></li>
            <li>API calls required: <strong>{(customers_to_process + batch_size - 1) // batch_size}</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Run analysis button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button(
            f"Analyze {customers_to_process} Customers",
            type="primary",
            use_container_width=True
        ):
            run_customer_analysis(customer_data.head(customers_to_process), batch_size)

def render_analysis_results_tab():
    """Render analysis results tab."""
    if st.session_state.analysis_results is None:
        st.info("No analysis results available. Please run analysis first.")
        return
    
    results = st.session_state.analysis_results
    customer_categories = results.get('customer_categories', [])
    aggregates = results.get('aggregates', {})
    
    # Results header
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Analysis Results
    </h3>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_analyzed = aggregates.get('total_customers', 0)
    upsell_eligible = aggregates.get('upsell_eligible_count', 0)
    vulnerable_count = aggregates.get('vulnerable_count', 0)
    accessibility_count = aggregates.get('accessibility_needs_count', 0)
    
    with col1:
        st.markdown(create_metric_card(
            "Customers Analyzed",
            f"{total_analyzed:,}",
            "100% complete",
            "positive"
        ), unsafe_allow_html=True)
    
    with col2:
        upsell_pct = (upsell_eligible / total_analyzed * 100) if total_analyzed > 0 else 0
        st.markdown(create_metric_card(
            "Upsell Eligible",
            f"{upsell_eligible:,}",
            f"{upsell_pct:.0f}% of base",
            "positive" if upsell_pct > 30 else "neutral"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Vulnerable",
            f"{vulnerable_count:,}",
            "Protected status",
            "neutral"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Accessibility Needs",
            f"{accessibility_count:,}",
            "Special support",
            "neutral"
        ), unsafe_allow_html=True)
    
    # Customer segments chart
    if aggregates.get('categories'):
        st.markdown("""
        <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
            Customer Segmentation
        </h4>
        """, unsafe_allow_html=True)
        
        categories = aggregates.get('categories', {})
        fig = go.Figure(data=[go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            hole=0.4,
            marker_colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
        )])
        fig.update_layout(
            font=dict(family="IBM Plex Sans"),
            height=350,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer details table
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Individual Customer Analysis
    </h4>
    """, unsafe_allow_html=True)
    
    # Create professional table
    customer_df = pd.DataFrame([{
        'Customer ID': c.get('customer_id', ''),
        'Name': c.get('name', ''),
        'Category': c.get('category', ''),
        'Upsell': 'Yes' if c.get('upsell_eligible') else 'No',
        'Health': c.get('financial_indicators', {}).get('account_health', ''),
        'Digital Maturity': c.get('financial_indicators', {}).get('digital_maturity', '')
    } for c in customer_categories])
    
    st.dataframe(customer_df, use_container_width=True, height=400)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = customer_df.to_csv(index=False)
        st.download_button(
            label="Export CSV",
            data=csv_data,
            file_name=f"customer_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="Export JSON",
            data=json_data,
            file_name=f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# ============================================================================
# UTILITY FUNCTIONS (keeping same functionality)
# ============================================================================

@st.cache_data
def load_customer_data():
    """Load customer data with caching."""
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None

def load_sample_data():
    """Load the sample customer data."""
    try:
        csv_path = Path("data/customer_profiles/sample_customers.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            return df
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
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def show_data_template():
    """Show the expected data template."""
    st.info("""
    **Required Fields:** customer_id, name, age, account_balance
    
    **Recommended Fields:** digital_logins_per_month, mobile_app_usage, email_opens_per_month, 
    phone_calls_per_month, branch_visits_per_month, prefers_digital, requires_support, 
    accessibility_needs, income_level, employment_status
    """)

def run_customer_analysis(customer_data, batch_size):
    """Run the AI customer analysis."""
    try:
        api_manager = APIManager()
    except Exception as e:
        st.error(f"Failed to initialize APIs: {str(e)}")
        return
    
    # Progress indicator
    with st.spinner("Analyzing customers with AI..."):
        customers_list = customer_data.to_dict('records')
        
        try:
            # Run the analysis
            analysis_results = api_manager.analyze_customer_base(
                customers_list, 
                batch_size=batch_size
            )
            
            if analysis_results:
                st.session_state.analysis_results = analysis_results
                st.success(f"Successfully analyzed {len(analysis_results.get('customer_categories', []))} customers")
                st.rerun()
            else:
                st.error("Analysis failed. Please check your API configuration.")
                
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Resonance Bank - Communication Intelligence",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply professional theme
    apply_professional_theme()
    
    # Render professional header
    render_professional_header()
    
    # Navigation
    selected_page = render_navigation_sidebar()
    
    # Route to appropriate page
    if selected_page == "Executive Dashboard":
        render_executive_dashboard()
    
    elif selected_page == "Customer Analysis":
        render_customer_analysis_page()
    
    elif selected_page == "Letter Management":
        # We'll update this module next
        from file_handlers.letter_scanner import render_enhanced_letter_management
        render_enhanced_letter_management()
    
    elif selected_page == "Batch Processing":
        batch_ui_renderer = get_batch_processing_ui()
        batch_ui_renderer()
    
    elif selected_page == "Cost Management":
        st.markdown(create_professional_card(
            "Cost Management",
            "Communication cost optimization and analysis"
        ), unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Configuration", "Analysis"])
        
        with tab1:
            render_cost_configuration_ui()
        
        with tab2:
            customer_categories = st.session_state.get("analysis_results", {}).get("customer_categories", [])
            render_cost_analyzer_ui(customer_categories)
    
    elif selected_page == "System Configuration":
        st.markdown(create_professional_card(
            "System Configuration",
            "API settings and system parameters"
        ), unsafe_allow_html=True)
        st.info("Configuration interface will be updated in the next iteration.")

if __name__ == "__main__":
    main()