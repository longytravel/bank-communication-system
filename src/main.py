"""
Main Streamlit Application with Lloyds Banking Group Branding
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Lloyds branding - MUST be before any other Streamlit commands
from branding.lloyds_brand import apply_lloyds_theme, get_lloyds_header, brand_manager

# Apply Lloyds theme immediately
apply_lloyds_theme()

# Now import your existing modules
from customer_analysis import render_customer_analysis_page
from file_handlers.letter_scanner import render_enhanced_letter_management
from communication_processing import get_customer_plans_ui_renderer

def main():
    """Main application with Lloyds branding."""
    
    # Inject Lloyds custom CSS on every page
    st.markdown(brand_manager.get_custom_css(), unsafe_allow_html=True)
    
    # Sidebar with Lloyds branding
    with st.sidebar:
        # Add Lloyds branded header in sidebar
        st.markdown("""
        <div style="background: #006A4D; color: white; padding: 1rem; 
                    margin: -1rem -1rem 1rem -1rem; text-align: center;">
            <h2 style="margin: 0;">🏦 Lloyds Banking Group</h2>
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Communication System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### Navigation")
        page = st.selectbox(
            "Select Module",
            ["🏠 Home", 
             "📊 Customer Analysis", 
             "📄 Letter Management", 
             "💬 Communication Plans"],
            label_visibility="collapsed"
        )
    
    # Main content area
    if page == "🏠 Home":
        # Use the branded header component
        st.markdown(get_lloyds_header(
            "Bank Communication System",
            "AI-powered customer engagement platform"
        ), unsafe_allow_html=True)
        
        # Welcome message with Lloyds styling
        st.markdown("""
        <div class="professional-card">
            <h3>Welcome to the Lloyds Banking Group Communication Platform</h3>
            <p>This system helps create personalized, cost-effective customer communications 
            using AI-powered analysis and multi-channel strategies.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards with Lloyds colors
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(brand_manager.create_metric_card(
                "Customer Analysis",
                "AI Segmentation",
                "Upload & analyze customer data"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(brand_manager.create_metric_card(
                "Letter Management",
                "Smart Classification",
                "Process regulatory & promotional content"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(brand_manager.create_metric_card(
                "Communication Plans",
                "Multi-channel",
                "Generate personalized strategies"
            ), unsafe_allow_html=True)
        
        # Quick start guide with Lloyds styling
        st.markdown("""
        <div style="background: #E8F4F0; padding: 1.5rem; border-radius: 8px; margin-top: 2rem;">
            <h3 style="color: #006A4D; margin-top: 0;">Quick Start Guide</h3>
            <ol style="color: #2D2D2D;">
                <li><strong>Upload Customer Data:</strong> Start with the Customer Analysis module</li>
                <li><strong>Classify Letters:</strong> Upload your communication templates</li>
                <li><strong>Generate Plans:</strong> Create personalized communication strategies</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer with Lloyds branding
        st.markdown("""
        <div style="margin-top: 3rem; padding: 1rem; border-top: 2px solid #006A4D; 
                    text-align: center; color: #666;">
            <p>© 2025 Lloyds Banking Group | Internal Use Only</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif page == "📊 Customer Analysis":
        render_customer_analysis_page()
    
    elif page == "📄 Letter Management":
        render_enhanced_letter_management()
    
    elif page == "💬 Communication Plans":
        # Get the renderer function and call it
        customer_plans_renderer = get_customer_plans_ui_renderer()
        customer_plans_renderer()

if __name__ == "__main__":
    # Set page config (this should be the first Streamlit command)
    st.set_page_config(
        page_title="Lloyds Banking Group - Communication System",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the main app
    main()