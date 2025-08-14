"""
Communication Cost System Integration
Complete module for integrating cost analysis into the bank communication system.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Integration with existing modules
from .cost_configuration import CostConfigurationManager
from .cost_integration import CostAnalyzer, render_cost_configuration_ui, render_cost_analyzer_ui

class CommunicationCostController:
    """Main controller for communication cost management."""
    
    def __init__(self):
        """Initialize cost controller."""
        self.cost_manager = CostConfigurationManager()
        self.cost_analyzer = CostAnalyzer()
    
    def optimize_communication_plan(self, communication_result: dict, 
                                  customer_profile: dict) -> dict:
        """Optimize communication plan with cost considerations."""
        
        # Get customer category
        customer_category = communication_result.get("customer_category", {}).get("label", "")
        
        # Get current timeline
        timeline = communication_result.get("comms_plan", {}).get("timeline", [])
        
        # Calculate costs for current plan
        current_costs = self._calculate_timeline_costs(timeline)
        
        # Apply cost optimizations
        optimized_timeline = self._apply_cost_optimizations(timeline, customer_category)
        optimized_costs = self._calculate_timeline_costs(optimized_timeline)
        
        # Add cost analysis to result
        communication_result["cost_analysis"] = {
            "original_cost": current_costs["total_cost"],
            "optimized_cost": optimized_costs["total_cost"],
            "savings": current_costs["total_cost"] - optimized_costs["total_cost"],
            "carbon_original": current_costs["total_carbon_kg"],
            "carbon_optimized": optimized_costs["total_carbon_kg"],
            "carbon_savings": current_costs["total_carbon_kg"] - optimized_costs["total_carbon_kg"],
            "channels_breakdown": optimized_costs["channels"],
            "scenario_used": self.cost_manager.current_scenario
        }
        
        # Update timeline with optimized version
        communication_result["comms_plan"]["timeline"] = optimized_timeline
        
        return communication_result
    
    def _calculate_timeline_costs(self, timeline: list) -> dict:
        """Calculate costs for a communication timeline."""
        
        channel_costs = {}
        total_cost = 0
        total_carbon = 0
        
        # Count channels in timeline
        channel_counts = {}
        for step in timeline:
            channel = step.get("channel", "").lower()
            if channel:
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        # Calculate costs for each channel
        for channel, count in channel_counts.items():
            if count > 0:
                # Map channels to cost calculator channels
                cost_channel = self._map_channel_for_costing(channel)
                if cost_channel:
                    calc = self.cost_manager.calculate_communication_cost(cost_channel, count)
                    channel_costs[channel] = calc
                    total_cost += calc["total_cost"]
                    total_carbon += calc["total_carbon_kg"]
        
        return {
            "total_cost": total_cost,
            "total_carbon_kg": total_carbon,
            "channels": channel_costs
        }
    
    def _map_channel_for_costing(self, channel: str) -> str:
        """Map timeline channel names to cost calculator channels."""
        
        mapping = {
            "email": "email",
            "sms": "sms", 
            "letter": "letter",
            "in_app": "in_app",
            "voice_note": "voice_note",
            "phone": None,  # No direct cost
            "braille": "letter",  # Similar cost to letter
            "audio": "voice_note"  # Similar to voice note
        }
        
        return mapping.get(channel.lower())
    
    def _apply_cost_optimizations(self, timeline: list, customer_category: str) -> list:
        """Apply cost optimizations while maintaining business rules."""
        
        optimized_timeline = timeline.copy()
        
        # Rule: Limit communication volume based on type
        classification = self._get_classification_from_timeline(timeline)
        
        if classification == "INFORMATION" and len(timeline) > 2:
            # Information: Max 2 channels
            optimized_timeline = self._limit_channels(optimized_timeline, 2, customer_category)
        elif classification == "REGULATORY" and len(timeline) > 2:
            # Regulatory: Max 2 channels (ensure durable medium)
            optimized_timeline = self._limit_channels_regulatory(optimized_timeline, customer_category)
        elif len(timeline) > 4:
            # Promotional: Max 4 channels
            optimized_timeline = self._limit_channels(optimized_timeline, 4, customer_category)
        
        return optimized_timeline
    
    def _get_classification_from_timeline(self, timeline: list) -> str:
        """Infer classification from timeline characteristics."""
        
        # Look for regulatory indicators
        for step in timeline:
            purpose = step.get("purpose", "").lower()
            if "regulatory" in purpose or "mandatory" in purpose:
                return "REGULATORY"
        
        # Look for promotional indicators
        has_multiple_channels = len(timeline) > 3
        has_upsell_channels = any("offer" in step.get("purpose", "").lower() for step in timeline)
        
        if has_multiple_channels or has_upsell_channels:
            return "PROMOTIONAL"
        
        return "INFORMATION"
    
    def _limit_channels(self, timeline: list, max_channels: int, customer_category: str) -> list:
        """Limit channels while preserving most important ones."""
        
        if len(timeline) <= max_channels:
            return timeline
        
        # Priority order based on customer category
        if customer_category == "Digital-first self-serve":
            priority = ["in_app", "email", "voice_note", "sms", "letter"]
        elif customer_category == "Vulnerable / extra-support":
            priority = ["letter", "phone", "email", "sms", "in_app"]
        elif customer_category == "Low/no-digital (offline-preferred)":
            priority = ["letter", "phone", "email", "in_app", "sms"]
        else:
            priority = ["email", "in_app", "sms", "letter", "phone"]
        
        # Sort timeline by priority
        def get_priority(step):
            channel = step.get("channel", "").lower()
            try:
                return priority.index(channel)
            except ValueError:
                return len(priority)  # Unknown channels go last
        
        sorted_timeline = sorted(timeline, key=get_priority)
        
        # Keep top channels and renumber
        limited_timeline = sorted_timeline[:max_channels]
        for i, step in enumerate(limited_timeline):
            step["step"] = i + 1
            if "cost_optimization" not in step:
                step["cost_optimization"] = "Channel prioritized for cost efficiency"
        
        return limited_timeline
    
    def _limit_channels_regulatory(self, timeline: list, customer_category: str) -> list:
        """Limit regulatory channels ensuring durable medium compliance."""
        
        if len(timeline) <= 2:
            return timeline
        
        # Ensure we have at least one durable medium
        durable_channels = ["letter", "email", "in_app"]
        
        # Find durable medium steps
        durable_steps = [step for step in timeline if step.get("channel", "").lower() in durable_channels]
        other_steps = [step for step in timeline if step.get("channel", "").lower() not in durable_channels]
        
        # Keep best durable medium + one other
        if customer_category == "Vulnerable / extra-support":
            # Prefer letter for vulnerable
            preferred_durable = [s for s in durable_steps if s.get("channel", "").lower() == "letter"]
            if not preferred_durable:
                preferred_durable = durable_steps[:1]
        else:
            # Prefer digital for others
            preferred_durable = [s for s in durable_steps if s.get("channel", "").lower() in ["email", "in_app"]][:1]
            if not preferred_durable:
                preferred_durable = durable_steps[:1]
        
        # Add one confirmation channel
        confirmation_step = other_steps[:1] if other_steps else []
        
        limited_timeline = preferred_durable + confirmation_step
        
        # Renumber
        for i, step in enumerate(limited_timeline):
            step["step"] = i + 1
            step["regulatory_compliance"] = "Regulatory durable medium requirement"
        
        return limited_timeline
    
    def get_cost_summary_for_batch(self, batch_results: list) -> dict:
        """Get cost summary for batch processing results."""
        
        total_cost = 0
        total_carbon = 0
        total_customers = len(batch_results)
        channel_usage = {}
        
        for result in batch_results:
            cost_analysis = result.get("result", {}).get("cost_analysis", {})
            
            if cost_analysis:
                total_cost += cost_analysis.get("optimized_cost", 0)
                total_carbon += cost_analysis.get("carbon_optimized", 0)
                
                # Aggregate channel usage
                channels = cost_analysis.get("channels_breakdown", {})
                for channel, data in channels.items():
                    if channel not in channel_usage:
                        channel_usage[channel] = {"volume": 0, "cost": 0}
                    channel_usage[channel]["volume"] += 1  # One per customer
                    channel_usage[channel]["cost"] += data.get("total_cost", 0)
        
        return {
            "total_cost": total_cost,
            "total_carbon_kg": total_carbon,
            "total_customers": total_customers,
            "cost_per_customer": total_cost / total_customers if total_customers > 0 else 0,
            "channel_usage": channel_usage,
            "scenario_used": self.cost_manager.current_scenario
        }

# Integration helper functions
def integrate_cost_analysis_with_api_manager(api_manager):
    """Integrate cost analysis with existing API manager."""
    
    cost_controller = CommunicationCostController()
    
    # Monkey patch the API manager to include cost analysis
    original_process_customer_communication = api_manager.process_customer_communication
    
    def enhanced_process_customer_communication(letter_text, customer_profile, channels, generate_voice=True):
        """Enhanced version that includes cost analysis."""
        
        # Get original result
        result = original_process_customer_communication(letter_text, customer_profile, channels, generate_voice)
        
        if result:
            # Add cost optimization
            result = cost_controller.optimize_communication_plan(result, customer_profile)
        
        return result
    
    # Replace method
    api_manager.process_customer_communication = enhanced_process_customer_communication
    
    return api_manager

def add_cost_tab_to_main_ui():
    """Add cost management tab to main UI."""
    
    import streamlit as st
    
    # This would be called from main.py
    with st.container():
        st.markdown("## 💰 Cost Management")
        
        tab1, tab2 = st.tabs(["Configuration", "Analysis"])
        
        with tab1:
            render_cost_configuration_ui()
        
        with tab2:
            # Get customer data from session state if available
            customer_categories = st.session_state.get("customer_analysis", {}).get("customer_categories", [])
            render_cost_analyzer_ui(customer_categories)

# Example usage for integration
def demo_cost_integration():
    """Demonstrate cost system integration."""
    
    print("🚀 Communication Cost System Demo")
    print("=" * 50)
    
    # Initialize cost controller
    cost_controller = CommunicationCostController()
    
    # Sample communication result
    sample_result = {
        "customer_category": {"label": "Digital-first self-serve"},
        "classification": {"label": "INFORMATION"},
        "comms_plan": {
            "timeline": [
                {"step": 1, "channel": "letter", "when": "immediate", "purpose": "Primary notification"},
                {"step": 2, "channel": "email", "when": "+1 hour", "purpose": "Email confirmation"},
                {"step": 3, "channel": "sms", "when": "+1 day", "purpose": "SMS reminder"},
                {"step": 4, "channel": "in_app", "when": "immediate", "purpose": "In-app notification"}
            ]
        }
    }
    
    # Optimize communication plan
    optimized_result = cost_controller.optimize_communication_plan(sample_result, {})
    
    # Display results
    cost_analysis = optimized_result["cost_analysis"]
    
    print(f"💰 Original cost: £{cost_analysis['original_cost']:.3f}")
    print(f"💰 Optimized cost: £{cost_analysis['optimized_cost']:.3f}")
    print(f"💰 Savings: £{cost_analysis['savings']:.3f}")
    print(f"🌱 Carbon saved: {cost_analysis['carbon_savings']:.3f}kg")
    
    print("\n📱 Optimized timeline:")
    for step in optimized_result["comms_plan"]["timeline"]:
        print(f"  {step['step']}. {step['channel'].upper()} - {step['purpose']}")

if __name__ == "__main__":
    demo_cost_integration()