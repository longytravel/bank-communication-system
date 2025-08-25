"""
Metrics Display Module
Handles the display of summary metrics and cost analysis.
"""

import streamlit as st
from typing import List, Dict

def render_summary_metrics(all_plans: List[Dict]):
    """Render summary metrics for all generated plans."""
    
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
    
    with col1:
        st.markdown(f"""
        <div style="background: #FEE2E2; border: 1px solid #EF4444; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #991B1B;">Traditional Approach</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #EF4444;">£{total_traditional:.2f}</div>
            <p style="color: #991B1B; margin-bottom: 0;">All letters (£{total_traditional/total_customers:.2f}/customer)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #DCFCE7; border: 1px solid #10B981; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #166534;">Optimized Strategy</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #10B981;">£{total_optimized:.2f}</div>
            <p style="color: #166534; margin-bottom: 0;">Smart channels (£{total_optimized/total_customers:.2f}/customer)</p>
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
        <div style="background: #F3E8FF; border: 1px solid #9333EA; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0; color: #581C87;">Customers Processed</h4>
            <div style="font-size: 1.5rem; font-weight: 700; color: #9333EA;">{total_customers}</div>
            <p style="color: #581C87; margin-bottom: 0;">Complete analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Channel usage summary (with video)
    st.markdown("### 📱 Channel Distribution")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📱 In-App", f"{total_in_app}", f"{total_in_app/total_customers*100:.0f}%")
    
    with col2:
        st.metric("📧 Email", f"{total_email}", f"{total_email/total_customers*100:.0f}%")
    
    with col3:
        st.metric("💬 SMS", f"{total_sms}", f"{total_sms/total_customers*100:.0f}%")
    
    with col4:
        st.metric("📮 Letter", f"{total_letter}", f"{total_letter/total_customers*100:.0f}%")
    
    with col5:
        st.metric("🔊 Voice", f"{total_voice}", f"{total_voice/total_customers*100:.0f}%")
    
    with col6:
        st.metric("🎬 Video", f"{total_video}", f"{total_video/total_customers*100:.0f}%")