"""
Batch Communication Processing UI
Streamlit interface for batch communication planning and cost analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from communication_processing.batch_planner import BatchCommunicationPlanner
from file_handlers.letter_scanner import EnhancedLetterScanner

def render_batch_communication_processing():
    """Main function to render batch communication processing page."""
    
    st.markdown("""
    <div class="modern-card">
        <h2 style="margin-top: 0; color: #1A1A1A;">💬 Batch Communication Processing</h2>
        <p style="color: #6B7280;">Create personalized communication plans for all customers and analyze cost savings vs traditional approach.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check prerequisites
    if not check_prerequisites():
        return
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📋 Setup Batch", "🚀 Process Communications", "📊 Results Analysis"])
    
    with tab1:
        render_batch_setup_tab()
    
    with tab2:
        render_batch_processing_tab()
    
    with tab3:
        render_results_analysis_tab()

def check_prerequisites():
    """Check if required data is available."""
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None
    
    # Check for letters
    scanner = EnhancedLetterScanner()
    letters = scanner.scan_all_letters()
    letters_available = len(letters) > 0
    
    if not customer_data_available or not letters_available:
        st.warning("📋 Prerequisites needed for batch processing:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not customer_data_available:
                st.error("❌ **Customer Analysis Required**")
                st.info("Go to 'Customer Analysis' tab and analyze your customer data first.")
            else:
                st.success("✅ Customer data ready")
        
        with col2:
            if not letters_available:
                st.error("❌ **Letters Required**")
                st.info("Go to 'Letter Management' tab and upload/create letters first.")
            else:
                st.success("✅ Letters available")
        
        return False
    
    return True

def render_batch_setup_tab():
    """Render batch setup configuration."""
    
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">📋 Batch Setup</h3>
        <p style="color: #6B7280;">Configure your batch communication processing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Customer data summary
    if 'analysis_results' in st.session_state:
        customer_categories = st.session_state.analysis_results.get('customer_categories', [])
        aggregates = st.session_state.analysis_results.get('aggregates', {})
        
        st.markdown("### 👥 Customer Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Customers", aggregates.get('total_customers', 0))
        
        with col2:
            st.metric("Upsell Eligible", aggregates.get('upsell_eligible_count', 0))
        
        with col3:
            st.metric("Vulnerable", aggregates.get('vulnerable_count', 0))
        
        with col4:
            st.metric("Digital-First", aggregates.get('categories', {}).get('Digital-first self-serve', 0))
        
        # Customer category breakdown
        categories = aggregates.get('categories', {})
        if categories:
            fig = px.pie(
                values=list(categories.values()),
                names=list(categories.keys()),
                title="Customer Category Distribution"
            )
            st.plotly_chart(fig, use_container_width=True, key="setup_categories_pie")
    
    # Letter selection
    st.markdown("### 📄 Letter Selection")
    
    scanner = EnhancedLetterScanner()
    letters = scanner.scan_all_letters()
    
    if letters:
        # Create letter options
        letter_options = []
        for letter in letters:
            classification = letter['classification']
            class_label = classification.get('classification', 'UNCLASSIFIED') if classification else 'UNCLASSIFIED'
            confidence = classification.get('confidence', 0) if classification else 0
            
            option_text = f"{letter['filename']} ({class_label}, Confidence: {confidence}/10)"
            letter_options.append(option_text)
        
        selected_letter_index = st.selectbox(
            "Select letter for batch processing:",
            range(len(letter_options)),
            format_func=lambda x: letter_options[x],
            help="Choose the letter that will be sent to all customers"
        )
        
        selected_letter = letters[selected_letter_index]
        
        # Display selected letter details
        classification = selected_letter['classification']
        if classification:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Classification", classification.get('classification', 'Unknown'))
            
            with col2:
                st.metric("Confidence", f"{classification.get('confidence', 0)}/10")
            
            with col3:
                st.metric("Word Count", classification.get('word_count', 0))
            
            # Show reasoning
            st.markdown("**Classification Reasoning:**")
            st.info(classification.get('reasoning', 'No reasoning provided'))
        
        # Preview letter content
        with st.expander("📖 Preview Letter Content"):
            content = scanner.read_letter_content(Path(selected_letter['filepath']))
            if content:
                st.text_area("Letter content:", content[:1000] + "..." if len(content) > 1000 else content, height=200, disabled=True)
        
        # Store selection in session state
        st.session_state.selected_letter = selected_letter
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_cost_optimization = st.checkbox(
                "Include cost optimization",
                value=True,
                help="Apply cost optimization rules to minimize communication costs"
            )
        
        with col2:
            generate_voice_notes = st.checkbox(
                "Generate voice notes",
                value=True,
                help="Generate voice notes for digital-first customers"
            )
        
        # Store processing options
        st.session_state.processing_options = {
            'include_cost_optimization': include_cost_optimization,
            'generate_voice_notes': generate_voice_notes
        }
        
        # Ready to process indicator
        if 'selected_letter' in st.session_state:
            st.success("✅ Ready to process batch communications!")
    else:
        st.warning("No letters available. Please upload letters in the Letter Management section.")

def render_batch_processing_tab():
    """Render batch processing execution."""
    
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">🚀 Process Communications</h3>
        <p style="color: #6B7280;">Execute batch communication planning for all customers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if setup is complete
    if 'selected_letter' not in st.session_state:
        st.warning("Please complete the batch setup first.")
        return
    
    if 'analysis_results' not in st.session_state:
        st.warning("Customer analysis results not found. Please analyze customers first.")
        return
    
    # Display processing summary
    customer_categories = st.session_state.analysis_results.get('customer_categories', [])
    selected_letter = st.session_state.selected_letter
    
    st.markdown("### 📊 Processing Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{len(customer_categories)}</div>
            <div class="metric-label">CUSTOMERS TO PROCESS</div>
            <div class="metric-delta positive">Ready for planning</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        classification = selected_letter['classification']
        class_label = classification.get('classification', 'UNCLASSIFIED') if classification else 'UNCLASSIFIED'
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{class_label}</div>
            <div class="metric-label">LETTER TYPE</div>
            <div class="metric-delta warning">{selected_letter['filename']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        processing_options = st.session_state.get('processing_options', {})
        optimizations = sum([
            processing_options.get('include_cost_optimization', False),
            processing_options.get('generate_voice_notes', False)
        ])
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{optimizations}</div>
            <div class="metric-label">OPTIMIZATIONS ENABLED</div>
            <div class="metric-delta positive">Cost & Voice</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Processing controls
    st.markdown("### 🎮 Processing Controls")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button(
            "🚀 Start Batch Processing",
            type="primary",
            use_container_width=True,
            disabled='batch_processing_results' in st.session_state
        ):
            execute_batch_processing()
    
    # Show processing status or results
    if 'batch_processing_results' in st.session_state:
        display_processing_results()

def execute_batch_processing():
    """Execute the batch communication processing."""
    
    st.markdown("""
    <div class="modern-card primary">
        <h3 style="margin-top: 0; color: white;">🔄 Batch Processing in Progress</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            Creating personalized communication plans for all customers...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Get data
        customer_categories = st.session_state.analysis_results.get('customer_categories', [])
        selected_letter = st.session_state.selected_letter
        
        status_text.text("🔍 Reading letter content...")
        progress_bar.progress(0.1)
        
        # Read letter content
        scanner = EnhancedLetterScanner()
        letter_text = scanner.read_letter_content(Path(selected_letter['filepath']))
        
        if not letter_text:
            st.error("Failed to read letter content.")
            return
        
        status_text.text("🧠 Initializing communication planner...")
        progress_bar.progress(0.2)
        
        # Initialize planner
        planner = BatchCommunicationPlanner()
        
        status_text.text("📋 Creating individual communication plans...")
        progress_bar.progress(0.4)
        
        # Create batch plans
        results = planner.create_batch_communication_plans(
            customer_categories,
            letter_text,
            selected_letter['classification'] or {'classification': 'INFORMATION'}
        )
        
        progress_bar.progress(0.8)
        status_text.text("💰 Calculating cost analysis...")
        
        if results and 'error' not in results:
            progress_bar.progress(1.0)
            status_text.text("✅ Batch processing complete!")
            
            # Store results
            st.session_state.batch_processing_results = results
            
            # Clear progress after 2 seconds
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"🎉 Successfully processed {len(customer_categories)} customers!")
            st.rerun()
        else:
            progress_bar.empty()
            status_text.empty()
            error_msg = results.get('error', 'Unknown error') if results else 'Processing failed'
            st.error(f"❌ Batch processing failed: {error_msg}")
    
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Processing error: {str(e)}")

def display_processing_results():
    """Display batch processing results summary."""
    
    results = st.session_state.batch_processing_results
    
    st.markdown("""
    <div class="modern-card primary">
        <h3 style="margin-top: 0; color: white;">✅ Batch Processing Complete</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    batch_metadata = results['batch_metadata']
    cost_analysis = results['cost_analysis']
    batch_summary = results['batch_summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{batch_metadata['total_customers']}</div>
            <div class="metric-label">CUSTOMERS PROCESSED</div>
            <div class="metric-delta positive">100% complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        savings_pct = cost_analysis['savings']['cost_savings_percentage']
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{savings_pct:.0f}%</div>
            <div class="metric-label">COST SAVINGS</div>
            <div class="metric-delta positive">vs traditional</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_channels = batch_summary['average_channels_per_customer']
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{avg_channels:.1f}</div>
            <div class="metric-label">AVG CHANNELS/CUSTOMER</div>
            <div class="metric-delta positive">Optimized</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        digital_pct = batch_summary['communication_efficiency']['digital_percentage']
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{digital_pct:.0f}%</div>
            <div class="metric-label">DIGITAL ADOPTION</div>
            <div class="metric-delta positive">vs traditional</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cost comparison chart
    st.markdown("### 💰 Cost Comparison")
    
    cost_data = [
        {
            'Approach': 'Traditional (Everyone gets letter)',
            'Cost': cost_analysis['traditional_approach']['total_cost'],
            'CO2 (kg)': cost_analysis['traditional_approach']['total_carbon_kg']
        },
        {
            'Approach': 'Optimized (Personalized)',
            'Cost': cost_analysis['optimized_approach']['total_cost'],
            'CO2 (kg)': cost_analysis['optimized_approach']['total_carbon_kg']
        }
    ]
    
    df_cost = pd.DataFrame(cost_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cost = px.bar(
            df_cost, 
            x='Approach', 
            y='Cost',
            title='Total Communication Costs',
            text='Cost'
        )
        fig_cost.update_traces(texttemplate='£%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_cost, use_container_width=True, key="results_cost_comparison")
    
    with col2:
        fig_carbon = px.bar(
            df_cost,
            x='Approach',
            y='CO2 (kg)',
            title='Carbon Footprint',
            text='CO2 (kg)'
        )
        fig_carbon.update_traces(texttemplate='%{text:.2f}kg', textposition='outside')
        st.plotly_chart(fig_carbon, use_container_width=True, key="results_carbon_comparison")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    recommendations = results.get('recommendations', [])
    for rec in recommendations:
        st.info(rec)
    
    # Action buttons
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Detailed Analysis", use_container_width=True):
            st.session_state.show_detailed_analysis = True
            st.rerun()
    
    with col2:
        # Prepare CSV data
        individual_plans = results['individual_plans']
        csv_data = prepare_csv_export(individual_plans)
        
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"batch_communication_plans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Prepare JSON data
        json_data = json.dumps(results, indent=2, default=str)
        
        st.download_button(
            label="🔄 Download JSON",
            data=json_data,
            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

def render_results_analysis_tab():
    """Render detailed results analysis."""
    
    if 'batch_processing_results' not in st.session_state:
        st.info("No batch processing results available. Please process communications first.")
        return
    
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">📊 Detailed Results Analysis</h3>
        <p style="color: #6B7280;">Comprehensive analysis of batch communication results.</p>
    </div>
    """, unsafe_allow_html=True)
    
    results = st.session_state.batch_processing_results
    individual_plans = results['individual_plans']
    batch_summary = results['batch_summary']
    cost_analysis = results['cost_analysis']
    
    # Channel usage analysis
    st.markdown("### 📱 Channel Usage Analysis")
    
    channel_popularity = batch_summary['channel_popularity']
    
    if channel_popularity:
        # Create channel usage chart
        channels_df = pd.DataFrame([
            {'Channel': channel.title(), 'Usage Count': count}
            for channel, count in channel_popularity.items()
        ])
        
        fig_channels = px.bar(
            channels_df,
            x='Channel',
            y='Usage Count',
            title='Communication Channel Usage Across All Customers',
            text='Usage Count'
        )
        fig_channels.update_traces(textposition='outside')
        st.plotly_chart(fig_channels, use_container_width=True, key="analysis_channel_usage")
    
    # Customer category breakdown
    st.markdown("### 👥 Customer Category Analysis")
    
    category_distribution = batch_summary['customer_distribution']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category pie chart
        if category_distribution:
            fig_categories = px.pie(
                values=list(category_distribution.values()),
                names=list(category_distribution.keys()),
                title="Customer Category Distribution"
            )
            st.plotly_chart(fig_categories, use_container_width=True, key="analysis_categories_pie")
    
    with col2:
        # Communication efficiency metrics
        efficiency = batch_summary['communication_efficiency']
        
        st.markdown("**Communication Efficiency:**")
        st.metric("Digital Percentage", f"{efficiency['digital_percentage']:.1f}%")
        st.metric("Traditional Percentage", f"{efficiency['traditional_percentage']:.1f}%")
        st.metric("Average Channels per Customer", f"{batch_summary['average_channels_per_customer']:.1f}")
    
    # Individual customer plans table
    st.markdown("### 👤 Individual Customer Plans")
    
    # Create summary table
    customer_summary = []
    
    for plan_data in individual_plans[:10]:  # Show first 10 customers
        customer_id = plan_data['customer_id']
        customer_name = plan_data['customer_name']
        category = plan_data['customer_category']
        
        plan = plan_data['plan']
        timeline = plan['communication_strategy'].get('comms_plan', {}).get('timeline', [])
        cost = plan['cost_breakdown']['total_cost']
        channels = [step.get('channel', '') for step in timeline]
        
        customer_summary.append({
            'Customer ID': customer_id,
            'Name': customer_name,
            'Category': category,
            'Channels': ', '.join(channels),
            'Channel Count': len(channels),
            'Cost (£)': f"{cost:.3f}",
            'Upsell': '✅' if plan['communication_strategy'].get('upsell_included') else '❌'
        })
    
    if customer_summary:
        df_summary = pd.DataFrame(customer_summary)
        st.dataframe(df_summary, use_container_width=True, height=400)
        
        if len(individual_plans) > 10:
            st.info(f"Showing first 10 of {len(individual_plans)} customers. Download CSV for complete data.")
    
    # Cost breakdown by channel
    st.markdown("### 💰 Cost Breakdown by Channel")
    
    channel_costs = cost_analysis['optimized_approach']['channel_usage']
    
    if channel_costs:
        cost_breakdown_data = []
        
        for channel, data in channel_costs.items():
            cost_breakdown_data.append({
                'Channel': channel.title(),
                'Customers Using': data['customers'],
                'Total Cost (£)': data['total_cost'],
                'Cost per Customer (£)': data['total_cost'] / data['customers'] if data['customers'] > 0 else 0
            })
        
        df_cost_breakdown = pd.DataFrame(cost_breakdown_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_cost_breakdown = px.bar(
                df_cost_breakdown,
                x='Channel',
                y='Total Cost (£)',
                title='Total Cost by Channel',
                text='Total Cost (£)'
            )
            fig_cost_breakdown.update_traces(texttemplate='£%{text:.3f}', textposition='outside')
            st.plotly_chart(fig_cost_breakdown, use_container_width=True, key="analysis_cost_breakdown")
        
        with col2:
            st.dataframe(df_cost_breakdown, use_container_width=True)
    
    # Scenario sensitivity analysis
    st.markdown("### 🎯 Cost Scenario Sensitivity")
    
    current_scenario = cost_analysis['scenario_used']
    st.info(f"Current analysis uses **{current_scenario}** cost scenario. Change scenarios in Cost Management to see different projections.")

def prepare_csv_export(individual_plans):
    """Prepare CSV data for export."""
    
    csv_data = []
    
    for plan_data in individual_plans:
        customer_id = plan_data['customer_id']
        customer_name = plan_data['customer_name']
        category = plan_data['customer_category']
        
        plan = plan_data['plan']
        timeline = plan['communication_strategy'].get('comms_plan', {}).get('timeline', [])
        cost_breakdown = plan['cost_breakdown']
        
        channels = [step.get('channel', '') for step in timeline]
        purposes = [step.get('purpose', '') for step in timeline]
        
        csv_data.append({
            'customer_id': customer_id,
            'customer_name': customer_name,
            'customer_category': category,
            'channels_used': ', '.join(channels),
            'channel_count': len(channels),
            'total_cost': cost_breakdown['total_cost'],
            'total_carbon_kg': cost_breakdown['total_carbon_kg'],
            'upsell_included': plan['communication_strategy'].get('upsell_included', False),
            'communication_purposes': ' | '.join(purposes[:3])  # First 3 purposes
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False)

# Main function for testing
def main():
    """Main function for testing batch communication processing."""
    st.set_page_config(
        page_title="Batch Communication Processing",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 Batch Communication Processing System")
    
    render_batch_communication_processing()

if __name__ == "__main__":
    main()