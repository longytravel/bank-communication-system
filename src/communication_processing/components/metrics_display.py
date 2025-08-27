"""
Metrics Display Module - FIXED
Handles the display of summary metrics and cost analysis.
"""

import streamlit as st
from typing import List, Dict

def render_summary_metrics(all_plans: List[Dict]):
    """Render summary metrics for all generated plans."""
    
    # Check if there are no plans
    if not all_plans or len(all_plans) == 0:
        st.warning("No communication plans have been generated yet. Please generate plans first.")
        return
    
    # Calculate totals
    total_customers = len(all_plans)
    total_traditional = sum(plan['costs']['traditional_total'] for plan in all_plans)
    total_optimized = sum(plan['costs']['optimized_total'] for plan in all_plans)
    total_savings = total_traditional - total_optimized
    savings_percentage = (total_savings / total_traditional * 100) if total_traditional > 0 else 0
    
    # Count channels used
    total_in_app = sum(1 for plan in all_plans if 'in_app' in plan['channels'])
    total_email = sum(1 for plan in all_plans if 'email' in plan['channels'])
    total_sms = sum(1 for plan in all_plans if 'sms' in plan['channels'])
    total_letter = sum(1 for plan in all_plans if 'letter' in plan['channels'])
    total_voice = sum(1 for plan in all_plans if 'voice_note' in plan['channels'])
    total_video = sum(1 for plan in all_plans if 'video_message' in plan['channels'])  # NEW
    
    # Display metrics
    st.markdown("### 💰 Cost Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate per-customer costs safely
    traditional_per_customer = total_traditional / total_customers if total_customers > 0 else 0
    optimized_per_customer = total_optimized / total_customers if total_customers > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div style="background: #FEE2E2; border: 1px solid #EF4444; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #991B1B;">Traditional Approach</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #EF4444;">£{total_traditional:.2f}</div>
            <p style="color: #991B1B; margin-bottom: 0;">All letters (£{traditional_per_customer:.2f}/customer)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #DCFCE7; border: 1px solid #10B981; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #166534;">Optimized Strategy</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #10B981;">£{total_optimized:.2f}</div>
            <p style="color: #166534; margin-bottom: 0;">Smart channels (£{optimized_per_customer:.2f}/customer)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #EFF6FF; border: 1px solid #3B82F6; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #1E40AF;">Total Savings</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #3B82F6;">£{total_savings:.2f}</div>
            <p style="color: #1E40AF; margin-bottom: 0;">{savings_percentage:.1f}% reduction</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #FFF4E6; border: 1px solid #F97316; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #9A3412;">Customers Processed</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #F97316;">{total_customers}</div>
            <p style="color: #9A3412; margin-bottom: 0;">Communication plans</p>
        </div>
        """, unsafe_allow_html=True)