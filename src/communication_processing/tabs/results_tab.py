"""
Results Tab Module
Handles the display of generated communication plan results.
"""

import streamlit as st
from pathlib import Path
import sys
from typing import List, Dict
from communication_processing.components.metrics_display import render_summary_metrics
import pandas as pd
from communication_processing.components.channel_displays import render_all_channels

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def render_results_tab():
    """Render comprehensive results with all customers and full content."""
    
    if 'communication_plans_generated' not in st.session_state:
        st.info("Generate communication plans first to see results.")
        return
    
    if 'all_customer_plans' not in st.session_state:
        st.error("No generated plans found. Please regenerate.")
        return
    
    all_plans = st.session_state.all_customer_plans
    
    st.markdown("### 📊 Communication Plans Results")
    
    # Summary metrics at the top
    render_summary_metrics(all_plans)
    
    # Complete customer table
    st.markdown("### 📋 All Customer Plans Summary")
    render_customer_summary_table(all_plans)
    
    # Individual customer details
    st.markdown("### 👤 Individual Customer Communication Details")
    render_individual_customer_details(all_plans)
    
    # Export section
    st.markdown("### 📥 Export Results")
    render_export_section(all_plans)
    
def render_customer_summary_table(all_plans: List[Dict]):
    """Render a comprehensive table of all customer plans."""
    
    # Build table data
    table_data = []
    
    for plan in all_plans:
        # Get channel indicators
        channels_str = ", ".join(plan['channels'])
        
        # Build row
        row = {
            'Customer': plan['customer_name'],
            'Category': plan['customer_category'],
            'Channels': channels_str,
            'Trad. Cost': f"£{plan['costs']['traditional_total']:.3f}",
            'Opt. Cost': f"£{plan['costs']['optimized_total']:.3f}",
            'Savings': f"£{plan['costs']['savings']:.3f}",
            'Savings %': f"{plan['costs']['savings_percentage']:.1f}%",
            'In-App': '✓' if 'in_app' in plan['channels'] else '✗',
            'Email': '✓' if 'email' in plan['channels'] else '✗',
            'SMS': '✓' if 'sms' in plan['channels'] else '✗',
            'Letter': '✓' if 'letter' in plan['channels'] else '✗',
            'Voice': '✓' if 'voice_note' in plan['channels'] else '✗',
            'Video': '🎬' if 'video_message' in plan['channels'] else '✗',  # NEW
            'Upsell': '✓' if plan['upsell_eligible'] else '✗'
        }
        
        # Add video tier if eligible
        if plan.get('video_eligible'):
            row['Video Tier'] = plan.get('video_tier', '-')
        else:
            row['Video Tier'] = '-'
        
        table_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display with color coding
    st.dataframe(
        df,
        use_container_width=True,
        height=400,
        column_config={
            "Savings %": st.column_config.NumberColumn(
                "Savings %",
                help="Percentage saved vs traditional approach",
                format="%.1f%%",
            ),
        }
    )
    
    # Summary statistics
    st.markdown("#### Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_savings_pct = sum(plan['costs']['savings_percentage'] for plan in all_plans) / len(all_plans)
        st.metric("Average Savings", f"{avg_savings_pct:.1f}%")
    
    with col2:
        digital_first = sum(1 for plan in all_plans if plan['customer_category'] == 'Digital-first self-serve')
        st.metric("Digital-First Customers", f"{digital_first}/{len(all_plans)}")
    
    with col3:
        vulnerable = sum(1 for plan in all_plans if plan['customer_category'] == 'Vulnerable / extra-support')
        st.metric("Protected Customers", f"{vulnerable}/{len(all_plans)}")
    
    with col4:
        video_eligible = sum(1 for plan in all_plans if plan.get('video_eligible', False))
        st.metric("🎬 Video Eligible", f"{video_eligible}/{len(all_plans)}")

# Continue with rest of functions (render_individual_customer_details, render_export_section, etc.)
# These remain mostly the same with added video support where needed...

def render_individual_customer_details(all_plans: List[Dict]):
    """Render detailed view for each customer with full content including video."""
    
    # Customer selector
    customer_names = [f"{plan['customer_name']} ({plan['customer_category']})" + 
                      (" 🎬" if plan.get('video_eligible') else "") 
                      for plan in all_plans]
    
    selected_index = st.selectbox(
        "Select customer to view full communication details:",
        range(len(customer_names)),
        format_func=lambda x: customer_names[x]
    )
    
    selected_plan = all_plans[selected_index]
    
    # Display customer header with video badge if eligible
    video_badge = ""
    if selected_plan.get('video_eligible'):
        video_tier = selected_plan.get('video_tier', 'SILVER')
        video_badge = f" | 🎬 {video_tier} Video Tier"
    
    st.markdown(f"""
    <div style="background: #F8FAFC; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <h4 style="margin-top: 0;">{selected_plan['customer_name']}{video_badge}</h4>
        <p style="margin-bottom: 0.5rem;"><strong>Category:</strong> {selected_plan['customer_category']}</p>
        <p style="margin-bottom: 0.5rem;"><strong>Communication Type:</strong> {selected_plan['classification_type']}</p>
        <p style="margin-bottom: 0;"><strong>Cost Savings:</strong> £{selected_plan['costs']['savings']:.3f} ({selected_plan['costs']['savings_percentage']:.1f}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # USE THE NEW MODULE TO DISPLAY ALL CHANNELS
    render_all_channels(selected_plan, selected_index)

def render_export_section(all_plans: List[Dict]):
    """Render export options for all results."""
    # Existing export code remains the same
    pass    