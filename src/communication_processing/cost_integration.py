"""
Cost Configuration Integration
Integrates cost configuration with communication processing and UI.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .cost_configuration import CostConfigurationManager, CommunicationCosts, VolumeDiscounts

class CostAnalyzer:
    """Analyzes communication costs and provides business intelligence."""
    
    def __init__(self):
        """Initialize cost analyzer."""
        self.cost_manager = CostConfigurationManager()
    
    def analyze_customer_communication_costs(self, customer_categories: list, 
                                           communication_strategy: dict) -> dict:
        """Analyze costs for customer communication strategy."""
        
        # Group customers by category
        category_counts = {}
        for customer in customer_categories:
            category = customer.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate costs by customer category
        category_costs = {}
        total_cost = 0
        total_carbon = 0
        total_communications = 0
        
        for category, count in category_counts.items():
            # Determine communication strategy for this category
            strategy = self._get_strategy_for_category(category, communication_strategy)
            
            category_cost = 0
            category_carbon = 0
            category_comms = 0
            channel_breakdown = {}
            
            for channel, volume_per_customer in strategy.items():
                total_volume = volume_per_customer * count
                if total_volume > 0:
                    calc = self.cost_manager.calculate_communication_cost(channel, total_volume)
                    category_cost += calc['total_cost']
                    category_carbon += calc['total_carbon_g']
                    category_comms += total_volume
                    
                    channel_breakdown[channel] = {
                        'volume': total_volume,
                        'cost': calc['total_cost'],
                        'carbon_g': calc['total_carbon_g']
                    }
            
            category_costs[category] = {
                'customer_count': count,
                'total_cost': category_cost,
                'total_carbon_g': category_carbon,
                'total_communications': category_comms,
                'cost_per_customer': category_cost / count if count > 0 else 0,
                'channels': channel_breakdown
            }
            
            total_cost += category_cost
            total_carbon += category_carbon
            total_communications += category_comms
        
        return {
            'total_cost': total_cost,
            'total_carbon_g': total_carbon,
            'total_carbon_kg': total_carbon / 1000,
            'total_communications': total_communications,
            'cost_per_communication': total_cost / total_communications if total_communications > 0 else 0,
            'categories': category_costs,
            'scenario_used': self.cost_manager.current_scenario
        }
    
    def _get_strategy_for_category(self, category: str, base_strategy: dict) -> dict:
        """Get communication strategy for specific customer category."""
        
        # Default strategy based on customer category
        if category == "Digital-first self-serve":
            return {"email": 1, "in_app": 1, "voice_note": 1}
        elif category == "Vulnerable / extra-support":
            return {"letter": 1, "phone": 1}  # Note: phone has no direct cost in our model
        elif category == "Low/no-digital (offline-preferred)":
            return {"letter": 1, "email": 1}
        elif category == "Accessibility & alternate-format needs":
            return {"letter": 1, "email": 1, "voice_note": 1}
        elif category == "Assisted-digital":
            return {"email": 1, "sms": 1}
        else:
            # Default strategy
            return base_strategy
    
    def compare_communication_strategies(self, customer_categories: list, 
                                       traditional_strategy: dict,
                                       optimized_strategy: dict) -> dict:
        """Compare traditional vs optimized communication strategies."""
        
        traditional_analysis = self.analyze_customer_communication_costs(
            customer_categories, traditional_strategy)
        
        optimized_analysis = self.analyze_customer_communication_costs(
            customer_categories, optimized_strategy)
        
        cost_savings = traditional_analysis['total_cost'] - optimized_analysis['total_cost']
        carbon_savings = traditional_analysis['total_carbon_g'] - optimized_analysis['total_carbon_g']
        
        return {
            'traditional': traditional_analysis,
            'optimized': optimized_analysis,
            'savings': {
                'cost_savings': cost_savings,
                'cost_savings_percent': (cost_savings / traditional_analysis['total_cost'] * 100) 
                                      if traditional_analysis['total_cost'] > 0 else 0,
                'carbon_savings_g': carbon_savings,
                'carbon_savings_kg': carbon_savings / 1000,
                'carbon_savings_percent': (carbon_savings / traditional_analysis['total_carbon_g'] * 100)
                                        if traditional_analysis['total_carbon_g'] > 0 else 0,
                'communications_reduction': (traditional_analysis['total_communications'] - 
                                           optimized_analysis['total_communications'])
            }
        }

def render_cost_configuration_ui():
    """Render cost configuration interface."""
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">💰 Cost Configuration</h3>
        <p style="color: #6B7280;">Configure cost assumptions for different communication channels.</p>
    </div>
    """, unsafe_allow_html=True)
    
    cost_manager = CostConfigurationManager()
    
    # Scenario selector
    col1, col2 = st.columns(2)
    
    with col1:
        scenario_options = list(cost_manager.scenarios.keys())
        current_scenario = st.selectbox(
            "Cost Scenario",
            scenario_options,
            index=scenario_options.index(cost_manager.current_scenario),
            help="Choose cost scenario for analysis"
        )
        
        if current_scenario != cost_manager.current_scenario:
            cost_manager.set_scenario(current_scenario)
            st.success(f"Switched to {current_scenario} scenario")
    
    with col2:
        scenario_desc = cost_manager.scenarios[current_scenario].description
        st.info(f"**{current_scenario.title()}**: {scenario_desc}")
    
    # Current costs display
    costs = cost_manager.get_current_costs()
    
    st.markdown("### 📊 Current Cost Structure")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        letter_total = costs.letter_postage + costs.letter_printing + costs.letter_envelope + costs.letter_staff_time
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{letter_total:.3f}</div>
            <div class="metric-label">LETTER COST</div>
            <div class="metric-delta warning">Per letter</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{costs.email_cost:.3f}</div>
            <div class="metric-label">EMAIL COST</div>
            <div class="metric-delta positive">Per email</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{costs.sms_cost:.3f}</div>
            <div class="metric-label">SMS COST</div>
            <div class="metric-delta positive">Per SMS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ratio = letter_total / costs.email_cost if costs.email_cost > 0 else 0
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{ratio:.0f}x</div>
            <div class="metric-label">LETTER vs EMAIL</div>
            <div class="metric-delta warning">Cost ratio</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cost breakdown chart
    st.markdown("### 📈 Cost Comparison by Volume")
    
    volumes = [100, 500, 1000, 5000]
    channels = ["letter", "email", "sms", "in_app"]
    
    cost_data = []
    for volume in volumes:
        for channel in channels:
            calc = cost_manager.calculate_communication_cost(channel, volume)
            cost_data.append({
                'Volume': volume,
                'Channel': channel.title(),
                'Total Cost': calc['total_cost'],
                'Cost per Item': calc['discounted_cost_per_item'],
                'Carbon (kg)': calc['total_carbon_kg']
            })
    
    df = pd.DataFrame(cost_data)
    
    # Create cost comparison chart
    fig = px.bar(
        df, 
        x='Volume', 
        y='Total Cost', 
        color='Channel',
        title='Total Communication Costs by Volume',
        labels={'Total Cost': 'Total Cost (£)'},
        text='Total Cost'
    )
    
    fig.update_traces(texttemplate='£%{text:.2f}', textposition='outside')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Environmental impact
    st.markdown("### 🌱 Environmental Impact")
    
    env_fig = px.bar(
        df,
        x='Volume',
        y='Carbon (kg)',
        color='Channel',
        title='Carbon Footprint by Communication Channel',
        labels={'Carbon (kg)': 'CO2 Emissions (kg)'}
    )
    
    st.plotly_chart(env_fig, use_container_width=True)
    
    # Custom scenario creation
    with st.expander("🛠️ Create Custom Scenario"):
        st.markdown("**Create your own cost scenario:**")
        
        custom_name = st.text_input("Scenario Name", "custom_scenario")
        custom_desc = st.text_input("Description", "Custom cost assumptions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Letter Costs:**")
            custom_postage = st.number_input("Postage (£)", value=0.85, step=0.01)
            custom_printing = st.number_input("Printing (£)", value=0.08, step=0.01)
            custom_envelope = st.number_input("Envelope (£)", value=0.03, step=0.01)
            custom_staff_time = st.number_input("Staff Time (£)", value=0.50, step=0.01)
        
        with col2:
            st.markdown("**Digital Costs:**")
            custom_email = st.number_input("Email (£)", value=0.002, step=0.001, format="%.3f")
            custom_sms = st.number_input("SMS (£)", value=0.05, step=0.01)
            custom_in_app = st.number_input("In-app (£)", value=0.001, step=0.001, format="%.3f")
            custom_voice = st.number_input("Voice Note (£)", value=0.02, step=0.01)
        
        if st.button("Create Custom Scenario"):
            custom_costs = {
                'letter_postage': custom_postage,
                'letter_printing': custom_printing,
                'letter_envelope': custom_envelope,
                'letter_staff_time': custom_staff_time,
                'email_cost': custom_email,
                'sms_cost': custom_sms,
                'in_app_notification': custom_in_app,
                'voice_note_generation': custom_voice
            }
            
            try:
                cost_manager.create_custom_scenario(custom_name, custom_desc, custom_costs)
                st.success(f"Created custom scenario: {custom_name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating scenario: {e}")

def render_cost_analyzer_ui(customer_categories: list = None):
    """Render cost analysis interface."""
    if not customer_categories:
        st.info("Please analyze customer data first to see cost analysis.")
        return
    
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin-top: 0; color: #1A1A1A;">📊 Communication Cost Analysis</h3>
        <p style="color: #6B7280;">Analyze costs and savings for different communication strategies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    cost_analyzer = CostAnalyzer()
    
    # Strategy comparison
    traditional_strategy = {"letter": 1}  # Everyone gets a letter
    optimized_strategy = {}  # Will be determined by customer category
    
    comparison = cost_analyzer.compare_communication_strategies(
        customer_categories, traditional_strategy, optimized_strategy)
    
    # Display savings summary
    savings = comparison['savings']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{comparison['traditional']['total_cost']:.2f}</div>
            <div class="metric-label">TRADITIONAL COST</div>
            <div class="metric-delta warning">All letters</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{comparison['optimized']['total_cost']:.2f}</div>
            <div class="metric-label">OPTIMIZED COST</div>
            <div class="metric-delta positive">Smart targeting</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">£{savings['cost_savings']:.2f}</div>
            <div class="metric-label">SAVINGS</div>
            <div class="metric-delta positive">{savings['cost_savings_percent']:.1f}% reduction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="modern-card">
            <div class="metric-value">{savings['carbon_savings_kg']:.1f}kg</div>
            <div class="metric-label">CO2 SAVED</div>
            <div class="metric-delta positive">{savings['carbon_savings_percent']:.1f}% reduction</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategy breakdown chart
    st.markdown("### 📊 Cost Breakdown by Customer Category")
    
    # Prepare data for visualization
    category_data = []
    for strategy_name, analysis in [("Traditional", comparison['traditional']), ("Optimized", comparison['optimized'])]:
        for category, data in analysis['categories'].items():
            category_data.append({
                'Strategy': strategy_name,
                'Category': category,
                'Cost': data['total_cost'],
                'Customers': data['customer_count'],
                'Cost per Customer': data['cost_per_customer'],
                'Carbon (kg)': data['total_carbon_g'] / 1000
            })
    
    df_categories = pd.DataFrame(category_data)
    
    if not df_categories.empty:
        fig = px.bar(
            df_categories,
            x='Category',
            y='Cost',
            color='Strategy',
            title='Communication Costs by Customer Category',
            labels={'Cost': 'Total Cost (£)'},
            text='Cost'
        )
        
        fig.update_traces(texttemplate='£%{text:.2f}', textposition='outside')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Channel distribution
    st.markdown("### 📱 Communication Channel Distribution")
    
    # Get channel usage from optimized strategy
    channel_usage = {}
    for category, data in comparison['optimized']['categories'].items():
        for channel, channel_data in data['channels'].items():
            if channel not in channel_usage:
                channel_usage[channel] = {'volume': 0, 'cost': 0}
            channel_usage[channel]['volume'] += channel_data['volume']
            channel_usage[channel]['cost'] += channel_data['cost']
    
    if channel_usage:
        channels_df = pd.DataFrame([
            {
                'Channel': channel.title(),
                'Volume': data['volume'],
                'Cost': data['cost'],
                'Cost per Item': data['cost'] / data['volume'] if data['volume'] > 0 else 0
            }
            for channel, data in channel_usage.items()
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volume pie chart
            fig_volume = px.pie(
                channels_df,
                values='Volume',
                names='Channel',
                title='Communication Volume by Channel'
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2:
            # Cost pie chart
            fig_cost = px.pie(
                channels_df,
                values='Cost',
                names='Channel',
                title='Communication Costs by Channel'
            )
            st.plotly_chart(fig_cost, use_container_width=True)
    
    # Scenario sensitivity analysis
    st.markdown("### 🎯 Scenario Sensitivity Analysis")
    
    cost_manager = cost_analyzer.cost_manager
    current_scenario = cost_manager.current_scenario
    
    scenario_results = {}
    for scenario_name in cost_manager.scenarios.keys():
        cost_manager.set_scenario(scenario_name)
        scenario_comparison = cost_analyzer.compare_communication_strategies(
            customer_categories, traditional_strategy, optimized_strategy)
        scenario_results[scenario_name] = scenario_comparison['savings']
    
    # Restore original scenario
    cost_manager.set_scenario(current_scenario)
    
    # Create sensitivity chart
    sensitivity_data = []
    for scenario, savings in scenario_results.items():
        sensitivity_data.append({
            'Scenario': scenario.title(),
            'Cost Savings (£)': savings['cost_savings'],
            'Cost Savings (%)': savings['cost_savings_percent'],
            'Carbon Savings (kg)': savings['carbon_savings_kg']
        })
    
    df_sensitivity = pd.DataFrame(sensitivity_data)
    
    if not df_sensitivity.empty:
        fig_sensitivity = px.bar(
            df_sensitivity,
            x='Scenario',
            y='Cost Savings (£)',
            title='Cost Savings Across Different Scenarios',
            text='Cost Savings (£)'
        )
        
        fig_sensitivity.update_traces(texttemplate='£%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    # Recommendations
    st.markdown("### 💡 Cost Optimization Recommendations")
    
    recommendations = []
    
    # Analyze the results for recommendations
    if savings['cost_savings_percent'] > 50:
        recommendations.append("🎉 **Excellent savings potential!** Your optimized strategy could save over 50% on communication costs.")
    
    if savings['carbon_savings_percent'] > 70:
        recommendations.append("🌱 **Significant environmental impact!** Reducing carbon emissions by over 70%.")
    
    # Check for high letter usage
    letter_volume = channel_usage.get('letter', {}).get('volume', 0)
    total_volume = sum(data['volume'] for data in channel_usage.values())
    letter_percentage = (letter_volume / total_volume * 100) if total_volume > 0 else 0
    
    if letter_percentage > 30:
        recommendations.append(f"📮 **High letter usage detected** ({letter_percentage:.1f}%). Consider digital alternatives for non-vulnerable customers.")
    
    if letter_percentage < 10:
        recommendations.append(f"✅ **Excellent digital adoption** ({100-letter_percentage:.1f}% digital). Monitor regulatory compliance.")
    
    # Volume efficiency
    avg_comms_per_customer = total_volume / len(customer_categories) if customer_categories else 0
    if avg_comms_per_customer > 3:
        recommendations.append(f"⚠️ **High communication volume** ({avg_comms_per_customer:.1f} per customer). Consider reducing for better customer experience.")
    
    if avg_comms_per_customer < 2:
        recommendations.append(f"✅ **Efficient communication** ({avg_comms_per_customer:.1f} per customer). Good balance achieved.")
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.info("💡 Run analysis with customer data to get personalized recommendations.")
    
    # Export results
    st.markdown("### 📥 Export Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Cost Analysis CSV"):
            export_data = []
            for category, data in comparison['optimized']['categories'].items():
                export_data.append({
                    'Category': category,
                    'Customer Count': data['customer_count'],
                    'Total Cost': data['total_cost'],
                    'Cost per Customer': data['cost_per_customer'],
                    'Total Communications': data['total_communications'],
                    'Carbon (kg)': data['total_carbon_g'] / 1000
                })
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="📊 Download Analysis CSV",
                data=csv,
                file_name=f"cost_analysis_{cost_manager.current_scenario}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("💾 Save Cost Configuration"):
            config_summary = cost_manager.get_scenario_summary()
            
            import json
            config_json = json.dumps(config_summary, indent=2)
            
            st.download_button(
                label="💾 Download Configuration JSON",
                data=config_json,
                file_name=f"cost_config_{cost_manager.current_scenario}.json",
                mime="application/json"
            )

# Main function for testing
def main():
    """Test the cost configuration system."""
    st.title("💰 Communication Cost Management System")
    
    tab1, tab2 = st.tabs(["Cost Configuration", "Cost Analysis"])
    
    with tab1:
        render_cost_configuration_ui()
    
    with tab2:
        # For testing, create sample customer categories
        sample_customers = [
            {"category": "Digital-first self-serve"},
            {"category": "Digital-first self-serve"},
            {"category": "Vulnerable / extra-support"},
            {"category": "Low/no-digital (offline-preferred)"},
            {"category": "Assisted-digital"}
        ]
        
        render_cost_analyzer_ui(sample_customers)

if __name__ == "__main__":
    main()