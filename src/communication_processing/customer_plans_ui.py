"""
Customer Communication Plans UI Module - WITH VIDEO SUPPORT
Personalized communication strategies with real AI content, in-app notifications, 
complete customer processing, comprehensive cost analysis, and VIDEO messages.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys
import time
import io
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.api_manager import APIManager
from ui.professional_theme import create_professional_card
from communication_processing.cost_configuration import CostConfigurationManager
from business_rules.video_rules import VideoEligibilityRules
from communication_processing.components.channel_displays import render_all_channels
from communication_processing.tabs.setup_tab import render_setup_tab
from communication_processing.tabs.generate_tab import render_generate_plans_tab
from communication_processing.tabs.results_tab import render_results_tab
from communication_processing.components.metrics_display import render_summary_metrics

def render_customer_communication_plans_page():
    """Render the Customer Communication Plans page with tabs."""
    
    st.markdown(create_professional_card(
        "Customer Communication Plans",
        "Create personalized, AI-generated communication strategies with real content, cost analysis, and video messages"
    ), unsafe_allow_html=True)
    
    # Check prerequisites first
    if not check_communication_prerequisites():
        return
    
    # Create tabs for the workflow
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Setup", "🚀 Generate Plans", "📊 Results", "📈 Analytics"])
    
    with tab1:
        render_setup_tab()
    
    with tab2:
        render_generate_plans_tab()
    
    with tab3:
        render_results_tab()
    
    with tab4:
        render_analytics_tab()

def check_communication_prerequisites():
    """Check if required data is available for communication planning."""
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None
    
    # Check for letters
    try:
        from file_handlers.letter_scanner import EnhancedLetterScanner
        scanner = EnhancedLetterScanner()
        letters = scanner.scan_all_letters()
        letters_available = len(letters) > 0
    except:
        letters_available = False
    
    if not customer_data_available or not letters_available:
        st.markdown("""
        <div style="background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="margin-top: 0; color: #92400E;">Prerequisites Required</h4>
            <p style="color: #92400E; margin-bottom: 0;">Complete the following before creating communication plans:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not customer_data_available:
                st.error("❌ Customer Analysis Required")
                st.markdown("Go to 'Customer Analysis' and analyze your customer data first.")
                
                # Add option to load test data
                st.markdown("---")
                st.markdown("**🧪 Or use test data for quick testing:**")
                
                if st.button("📊 Load 3 Test Customers", type="primary", use_container_width=True):
                    try:
                        import json
                        from pathlib import Path
                        test_file = Path("data/test_data/test_customers_analyzed.json")
                        if test_file.exists():
                            with open(test_file, 'r') as f:
                                test_data = json.load(f)
                            
                            # Store in analysis_results as before
                            st.session_state.analysis_results = test_data
                            
                            # ALSO store customer_categories directly for the Generate tab
                            st.session_state.customer_categories = test_data.get('customer_categories', [])
                            
                            # Set a flag that analysis is completed
                            st.session_state.analysis_completed = True
                            
                            st.success("✅ Test dataset loaded successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Test dataset file not found. Run create_test_dataset.py first.")
                    except Exception as e:
                        st.error(f"Error loading test data: {e}")
                
                st.info("Test customers: Maria (Spanish), Vera (Vulnerable), Dave (Premium)")
                
            else:
                st.success("✅ Customer Data Ready")
                st.markdown("Customer analysis completed and available.")
                
                # Show option to switch to test data if wanted
                with st.expander("🧪 Switch to test data"):
                    if st.button("Load Test Dataset Instead", use_container_width=True):
                        try:
                            import json
                            from pathlib import Path
                            test_file = Path("data/test_data/test_customers_analyzed.json")
                            if test_file.exists():
                                with open(test_file, 'r') as f:
                                    test_data = json.load(f)
                                
                                # Store properly for all tabs
                                st.session_state.analysis_results = test_data
                                st.session_state.customer_categories = test_data.get('customer_categories', [])
                                st.session_state.analysis_completed = True
                                
                                st.success("✅ Switched to test dataset!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        with col2:
            if not letters_available:
                st.error("❌ Letters Required")
                st.markdown("Go to 'Letter Management' and upload/create letters first.")
            else:
                st.success("✅ Letters Available")
                st.markdown(f"{len(letters)} letters ready for processing.")
        
        # Show currently loaded data info
        if customer_data_available:
            st.markdown("---")
            st.markdown("**📊 Current Data:**")
            if 'analysis_results' in st.session_state:
                customers = st.session_state.analysis_results.get('customer_categories', [])
                if len(customers) == 3:
                    # Likely test data
                    customer_names = [c.get('name', 'Unknown') for c in customers[:3]]
                    st.info(f"Test Data: {', '.join(customer_names)}")
                else:
                    st.info(f"Production Data: {len(customers)} customers")
        
        return False
    
    return True

def show_generation_success():
    """Show generation success message."""
    
    st.markdown("""
    <div style="background: #10B981; color: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">✅ Generation Complete!</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            All customer communication plans have been created. Go to the "Results" tab to view them.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 View Results", use_container_width=True):
            pass  # Will switch to results tab on rerun
    
    with col2:
        if st.button("🔄 Generate New Plans", use_container_width=True, type="secondary"):
            if 'communication_plans_generated' in st.session_state:
                del st.session_state.communication_plans_generated
            if 'generated_plans_data' in st.session_state:
                del st.session_state.generated_plans_data
            if 'all_customer_plans' in st.session_state:
                del st.session_state.all_customer_plans
            st.rerun()

def render_analytics_tab():
    """Render analytics and insights tab."""
    
    if 'all_customer_plans' not in st.session_state:
        st.info("Generate communication plans first to see analytics.")
        return
    
    st.markdown("### 📈 Analytics & Insights")
    
    # Get the data
    all_plans = st.session_state.all_customer_plans
    
    if not all_plans:
        st.warning("No plans available for analysis.")
        return
    
    # Calculate statistics
    total_customers = len(all_plans)
    total_savings = sum(plan['costs']['savings'] for plan in all_plans)
    avg_savings_pct = sum(plan['costs']['savings_percentage'] for plan in all_plans) / len(all_plans)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col2:
        st.metric("Total Savings", f"£{total_savings:.2f}")
    
    with col3:
        st.metric("Average Savings", f"{avg_savings_pct:.1f}%")
    
    with col4:
        video_eligible = sum(1 for plan in all_plans if plan.get('video_eligible', False))
        st.metric("Video Eligible", f"{video_eligible}")
    
    # Channel distribution
    st.markdown("### Channel Usage Distribution")
    
    channel_counts = {}
    for plan in all_plans:
        for channel in plan['channels']:
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
    
    if channel_counts:
        df_channels = pd.DataFrame(
            list(channel_counts.items()),
            columns=['Channel', 'Count']
        )
        df_channels = df_channels.sort_values('Count', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df_channels.set_index('Channel'))
        with col2:
            st.dataframe(df_channels, hide_index=True, use_container_width=True)
    
    # Category breakdown
    st.markdown("### Customer Category Analysis")
    
    category_stats = {}
    for plan in all_plans:
        cat = plan['customer_category']
        if cat not in category_stats:
            category_stats[cat] = {
                'count': 0,
                'total_savings': 0,
                'channels': []
            }
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_savings'] += plan['costs']['savings']
        category_stats[cat]['channels'].extend(plan['channels'])
    
    # Display category table
    category_data = []
    for cat, stats in category_stats.items():
        unique_channels = list(set(stats['channels']))
        category_data.append({
            'Category': cat,
            'Customers': stats['count'],
            'Total Savings': f"£{stats['total_savings']:.2f}",
            'Avg Savings': f"£{stats['total_savings']/stats['count']:.2f}",
            'Primary Channels': ', '.join(unique_channels[:3])
        })
    
    df_categories = pd.DataFrame(category_data)
    st.dataframe(df_categories, hide_index=True, use_container_width=True)