"""
Resonance Bank - Professional Banking Communication Platform
Enterprise-grade banking interface with AI-powered communication intelligence.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config, is_configured
from api.api_manager import APIManager

# Import the professional theme
from ui.professional_theme import (
    apply_professional_theme,
    render_professional_header,
    create_status_badge,
    create_professional_card
)

# Import the three core modules
from customer_analysis import render_customer_analysis_page as render_customer_analysis_module
from file_handlers.letter_scanner import render_enhanced_letter_management
from communication_processing import get_customer_plans_ui_renderer

# ============================================================================
# NAVIGATION
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
            "Customer Analysis": "AI-powered customer segmentation",
            "Letter Management": "Document classification and management",
            "Customer Communication Plans": "Personalized communication strategies with real AI content"
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
# UTILITY FUNCTIONS (Keep only if needed by other modules)
# ============================================================================

@st.cache_data
def load_customer_data():
    """Load customer data with caching."""
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None

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
    if selected_page == "Customer Analysis":
        render_customer_analysis_module()
    
    elif selected_page == "Letter Management":
        render_enhanced_letter_management()
        
    elif selected_page == "Customer Communication Plans":
        customer_plans_renderer = get_customer_plans_ui_renderer()
        customer_plans_renderer()

if __name__ == "__main__":
    main()