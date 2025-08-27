"""
Results Tab Module - FIXED
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
    
    # Check if plans have been generated
    if 'communication_plans_generated' not in st.session_state:
        st.info("Generate communication plans first to see results.")
        return
    
    if 'all_customer_plans' not in st.session_state:
        st.error("No generated plans found. Please regenerate.")
        return
    
    all_plans = st.session_state.all_customer_plans
    
    # Check if plans list is empty
    if not all_plans or len(all_plans) == 0:
        st.warning("No customer plans available. Please generate plans in the 'Generate Plans' tab first.")
        return
    
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
    
    # Safety check for empty plans
    if not all_plans or len(all_plans) == 0:
        st.info("No customer plans to display.")
        return
    
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
            'Savings %': f"{plan['costs']['savings_percentage']:.1f}%"
        }
        
        # Add upsell indicator if applicable
        if plan.get('upsell_eligible', False):
            row['Upsell'] = "✅"
        else:
            row['Upsell'] = ""
            
        # Add video indicator if applicable
        if plan.get('video_eligible', False):
            row['Video'] = f"🎬 {plan.get('video_tier', 'Yes')}"
        else:
            row['Video'] = ""
        
        table_data.append(row)
    
    # Create DataFrame and display
    df = pd.DataFrame(table_data)
    
    # Calculate summary stats safely
    total_traditional = sum(plan['costs']['traditional_total'] for plan in all_plans)
    total_optimized = sum(plan['costs']['optimized_total'] for plan in all_plans)
    total_savings = total_traditional - total_optimized
    
    # Calculate average savings percentage safely
    if len(all_plans) > 0:
        avg_savings_pct = sum(plan['costs']['savings_percentage'] for plan in all_plans) / len(all_plans)
    else:
        avg_savings_pct = 0
    
    # Display summary row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Traditional", f"£{total_traditional:.2f}")
    with col2:
        st.metric("Total Optimized", f"£{total_optimized:.2f}")
    with col3:
        st.metric("Total Savings", f"£{total_savings:.2f}")
    with col4:
        st.metric("Avg Savings", f"{avg_savings_pct:.1f}%")
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Savings': st.column_config.NumberColumn(format="£%.3f"),
            'Savings %': st.column_config.NumberColumn(format="%.1f%%")
        }
    )
    
def render_individual_customer_details(all_plans: List[Dict]):
    """Render detailed view of individual customer communications."""
    
    if not all_plans:
        st.info("No customer details to display.")
        return
        
    # Create tabs for each customer (limit to first 10 for performance)
    num_customers = min(len(all_plans), 10)
    
    if num_customers > 0:
        customer_tabs = st.tabs([f"{plan['customer_name']}" for plan in all_plans[:num_customers]])
        
        for idx, tab in enumerate(customer_tabs):
            with tab:
                plan = all_plans[idx]
                render_single_customer_detail(plan)
    
    if len(all_plans) > 10:
        st.info(f"Showing first 10 customers. Total: {len(all_plans)} customers.")

def render_single_customer_detail(plan: Dict):
    """Render details for a single customer."""
    
    # Customer header
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"**Category:** {plan['customer_category']}")
    with col2:
        st.markdown(f"**Classification:** {plan['classification_type']}")
    with col3:
        if plan.get('upsell_eligible'):
            st.markdown("**✅ Upsell Eligible**")
    with col4:
        if plan.get('video_eligible'):
            st.markdown(f"**🎬 Video Tier: {plan.get('video_tier', 'Yes')}**")
    
    # Cost breakdown
    st.markdown("#### Cost Analysis")
    cost_col1, cost_col2, cost_col3 = st.columns(3)
    
    with cost_col1:
        st.metric("Traditional", f"£{plan['costs']['traditional_total']:.3f}")
    with cost_col2:
        st.metric("Optimized", f"£{plan['costs']['optimized_total']:.3f}")
    with cost_col3:
        st.metric("Savings", f"£{plan['costs']['savings']:.3f} ({plan['costs']['savings_percentage']:.1f}%)")
    
    # Channel content
    st.markdown("#### Communication Content")
    
    # Display all channels using the channel display component
    render_all_channels(plan, 0)

def render_export_section(all_plans: List[Dict]):
    """Render export options for the results."""
    
    if not all_plans:
        st.info("No data to export.")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            # Create Excel export logic here
            st.success("Excel export would be generated here")
    
    with col2:
        if st.button("📄 Export to PDF", use_container_width=True):
            # Create PDF export logic here
            st.success("PDF export would be generated here")