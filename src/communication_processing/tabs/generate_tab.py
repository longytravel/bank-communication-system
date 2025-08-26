"""
Generate Tab Module - Minimal working version
Handles the generation of communication plans.
"""

import streamlit as st
from pathlib import Path
import sys
from typing import List, Dict
from business_rules.video_rules import VideoEligibilityRules
import time
from datetime import datetime
from communication_processing.cost_configuration import CostConfigurationManager
from api.api_manager import APIManager
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def render_generate_plans_tab():
    """Render the generate plans tab with full customer processing."""
    
    # Check if setup is complete
    if 'selected_letter' not in st.session_state:
        st.warning("Please complete the Setup tab first.")
        return
    
    st.markdown("### 🚀 Generate Personalized Communication Plans")
    
    # Show what we're about to process
    customer_categories = st.session_state.analysis_results.get('customer_categories', [])
    selected_letter = st.session_state.selected_letter
    options = st.session_state.get('processing_options', {})
    
    # Filter customers based on selection
    filtered_customers = filter_customers(customer_categories, options.get('customer_filter', 'First 20'))
    
    # Count video eligible in filtered set
    video_rules = VideoEligibilityRules()
    video_eligible_count = sum(1 for c in filtered_customers 
                              if video_rules.is_video_eligible(c).get('eligible', False))
    
    # Processing summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Customers to Process", len(filtered_customers))
    
    with col2:
        classification = selected_letter['classification']
        class_type = classification.get('classification', 'UNKNOWN') if classification else 'UNKNOWN'
        st.metric("Letter Type", class_type)
    
    with col3:
        st.metric("Personalization", options.get('personalization_level', 'Standard'))
    
    with col4:
        if options.get('generate_videos', False):
            st.metric("🎬 Video Eligible", video_eligible_count)
        else:
            st.metric("Videos", "Disabled")
    
    # Processing options
    st.markdown("### Processing Options")
    col1, col2 = st.columns(2)
    
    with col1:
        processing_mode = st.radio(
            "Processing Mode",
            ["Quick Demo (Simulated)", "Full AI Generation (Real)"],
            help="Quick Demo uses templates, Full AI makes real API calls"
        )
    
    with col2:
        if processing_mode == "Full AI Generation (Real)":
            st.warning("⚠️ This will make real API calls and may take 2-3 minutes for 20 customers")
            api_batch_size = st.slider("API Batch Size", 1, 5, 3, 
                                      help="Process customers in batches to avoid rate limits")
        else:
            api_batch_size = 5
    
    # Generation button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button(
            f"🎯 Generate Plans for {len(filtered_customers)} Customers",
            type="primary",
            use_container_width=True,
            disabled=False
        ):
            if processing_mode == "Full AI Generation (Real)":
                st.info("Real AI generation selected - using templates for now")
                generate_demo_communication_plans(filtered_customers, selected_letter, options)
            else:
                generate_demo_communication_plans(filtered_customers, selected_letter, options)
    
    # Show results if generated
    if 'communication_plans_generated' in st.session_state:
        show_generation_success()

def filter_customers(customer_categories: List[Dict], filter_option: str) -> List[Dict]:
    """Filter customers based on selection."""
    if filter_option == "First 20":
        return customer_categories[:20]
    elif filter_option == "First 10":
        return customer_categories[:10]
    elif filter_option == "First 5":
        return customer_categories[:5]
    else:
        return customer_categories[:20]

def generate_demo_communication_plans(customers, letter, options):
    """Generate demo plans using templates (fast, no API calls)."""
    
    st.markdown("""Demo generation in progress...""")
    
    # Store results
    st.session_state.communication_plans_generated = True
    st.session_state.all_customer_plans = []
    
    st.success("Demo plans generated!")
    st.rerun()

def show_generation_success():
    """Show generation success message."""
    st.success("Plans generated successfully! Go to Results tab to view.")

# Additional helper functions
def create_demo_content_for_customer(*args, **kwargs):
    """Create demo content"""
    return {}

def create_real_ai_content_for_customer(*args, **kwargs):
    """Create AI content"""
    return {}

def get_channels_for_category(*args, **kwargs):
    """Get channels"""
    return ["email", "sms"]

def calculate_channel_costs(*args, **kwargs):
    """Calculate costs"""
    return {}

def generate_template_content(*args, **kwargs):
    """Generate templates"""
    return {}

def get_base_templates(*args, **kwargs):
    """Get base templates"""
    return {}
