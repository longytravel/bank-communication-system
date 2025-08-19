"""
Cost Configuration Integration
Professional UI for cost management and analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import professional theme components
from ui.professional_theme import (
    create_metric_card,
    create_status_badge,
    create_professional_card
)

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
    """Render professional cost configuration interface."""
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Cost Configuration
    </h3>
    <p style="color: #64748B; font-size: 0.875rem; margin-bottom: 1.5rem;">
        Configure cost assumptions for different communication channels.
    </p>
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
    
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Current Cost Structure
    </h4>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        letter_total = costs.letter_postage + costs.letter_printing + costs.letter_envelope + costs.letter_staff_time
        st.markdown(create_metric_card(
            "Letter Cost",
            f"£{letter_total:.3f}",
            "Per letter"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Email Cost",
            f"£{costs.email_cost:.3f}",
            "Per email"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "SMS Cost",
            f"£{costs.sms_cost:.3f}",
            "Per SMS"
        ), unsafe_allow_html=True)
    
    with col4:
        ratio = letter_total / costs.email_cost if costs.email_cost > 0 else 0
        st.markdown(create_metric_card(
            "Letter vs Email",
            f"{ratio:.0f}x",
            "Cost ratio"
        ), unsafe_allow_html=True)
    
    # Cost breakdown chart
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Cost Comparison by Volume
    </h4>
    """, unsafe_allow_html=True)
    
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
        text='Total Cost',
        color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
    )
    
    fig.update_traces(texttemplate='£%{text:.2f}', textposition='outside')
    fig.update_layout(
        height=400,
        font=dict(family="IBM Plex Sans"),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Environmental impact
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Environmental Impact
    </h4>
    """, unsafe_allow_html=True)
    
    env_fig = px.bar(
        df,
        x='Volume',
        y='Carbon (kg)',
        color='Channel',
        title='Carbon Footprint by Communication Channel',
        labels={'Carbon (kg)': 'CO2 Emissions (kg)'},
        color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
    )
    
    env_fig.update_layout(
        height=400,
        font=dict(family="IBM Plex Sans"),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(env_fig, use_container_width=True)

def render_cost_analyzer_ui(customer_categories: list = None):
    """Render professional cost analysis interface."""
    if not customer_categories:
        st.info("Please analyze customer data first to see cost analysis.")
        return
    
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Communication Cost Analysis
    </h3>
    <p style="color: #64748B; font-size: 0.875rem; margin-bottom: 1.5rem;">
        Analyze costs and savings for different communication strategies.
    </p>
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
        st.markdown(create_metric_card(
            "Traditional Cost",
            f"£{comparison['traditional']['total_cost']:.2f}",
            "All letters"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Optimized Cost",
            f"£{comparison['optimized']['total_cost']:.2f}",
            "Smart targeting"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Savings",
            f"£{savings['cost_savings']:.2f}",
            f"{savings['cost_savings_percent']:.1f}% reduction",
            "positive"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "CO2 Saved",
            f"{savings['carbon_savings_kg']:.1f}kg",
            f"{savings['carbon_savings_percent']:.1f}% reduction",
            "positive"
        ), unsafe_allow_html=True)
    
    # Strategy breakdown chart
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Cost Breakdown by Customer Category
    </h4>
    """, unsafe_allow_html=True)
    
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
            text='Cost',
            barmode='group',
            color_discrete_sequence=['#E2E8F0', '#3B82F6']
        )
        
        fig.update_traces(texttemplate='£%{text:.2f}', textposition='outside')
        fig.update_layout(
            height=400,
            xaxis_tickangle=-45,
            font=dict(family="IBM Plex Sans"),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Channel distribution
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Communication Channel Distribution
    </h4>
    """, unsafe_allow_html=True)
    
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
            fig_volume = go.Figure(data=[go.Pie(
                labels=channels_df['Channel'],
                values=channels_df['Volume'],
                hole=0.4,
                marker_colors=['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
            )])
            fig_volume.update_layout(
                title="Communication Volume by Channel",
                font=dict(family="IBM Plex Sans"),
                height=350
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2:
            # Cost pie chart
            fig_cost = go.Figure(data=[go.Pie(
                labels=channels_df['Channel'],
                values=channels_df['Cost'],
                hole=0.4,
                marker_colors=['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
            )])
            fig_cost.update_layout(
                title="Communication Costs by Channel",
                font=dict(family="IBM Plex Sans"),
                height=350
            )
            st.plotly_chart(fig_cost, use_container_width=True)
    
    # Recommendations
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Cost Optimization Recommendations
    </h4>
    """, unsafe_allow_html=True)
    
    recommendations = []
    
    # Analyze the results for recommendations
    if savings['cost_savings_percent'] > 50:
        recommendations.append({
            "priority": "high",
            "text": f"Excellent savings potential: Your optimized strategy could save over {savings['cost_savings_percent']:.0f}% on communication costs."
        })
    
    if savings['carbon_savings_percent'] > 70:
        recommendations.append({
            "priority": "high",
            "text": f"Significant environmental impact: Reducing carbon emissions by {savings['carbon_savings_percent']:.0f}%."
        })
    
    # Check for high letter usage
    letter_volume = channel_usage.get('letter', {}).get('volume', 0)
    total_volume = sum(data['volume'] for data in channel_usage.values())
    letter_percentage = (letter_volume / total_volume * 100) if total_volume > 0 else 0
    
    if letter_percentage > 30:
        recommendations.append({
            "priority": "medium",
            "text": f"High letter usage detected ({letter_percentage:.1f}%). Consider digital alternatives for non-vulnerable customers."
        })
    
    if letter_percentage < 10:
        recommendations.append({
            "priority": "low",
            "text": f"Excellent digital adoption ({100-letter_percentage:.1f}% digital). Monitor regulatory compliance."
        })
    
    # Display recommendations
    for rec in recommendations:
        color = "#10B981" if rec["priority"] == "high" else "#F59E0B" if rec["priority"] == "medium" else "#3B82F6"
        st.markdown(f"""
        <div style="padding: 0.75rem; border-left: 3px solid {color}; 
                    background: #F8FAFC; margin-bottom: 0.5rem; border-radius: 0 6px 6px 0;">
            <div style="color: #0F172A; font-size: 0.875rem;">{rec["text"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Export results
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Export Analysis
    </h4>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
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
            label="Export Cost Analysis CSV",
            data=csv,
            file_name=f"cost_analysis_{cost_analyzer.cost_manager.current_scenario}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        import json
        config_summary = {
            "scenario": cost_analyzer.cost_manager.current_scenario,
            "savings": savings,
            "channel_usage": channel_usage
        }
        
        config_json = json.dumps(config_summary, indent=2)
        
        st.download_button(
            label="Export Configuration JSON",
            data=config_json,
            file_name=f"cost_config_{cost_analyzer.cost_manager.current_scenario}.json",
            mime="application/json",
            use_container_width=True
        )