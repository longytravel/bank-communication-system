"""
Batch Communication Planner
Generates unique communication plans for each customer based on their category and letter type.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.api_manager import APIManager
from business_rules.engine import BusinessRulesEngine
from communication_processing.cost_configuration import CostConfigurationManager

class BatchCommunicationPlanner:
    """
    Creates unique communication plans for batches of customers.
    Each customer gets a personalized plan based on their category and the letter type.
    """
    
    def __init__(self):
        """Initialize the batch communication planner."""
        self.logger = logging.getLogger(__name__)
        
        self.api_manager = None
        self.business_rules = BusinessRulesEngine()
        self.cost_manager = CostConfigurationManager()
        
        # Standard communication strategies by customer category
        self.category_strategies = {
            "Digital-first self-serve": {
                "channels": ["in_app", "email", "voice_note"],
                "priority": "digital_first",
                "max_channels": 3
            },
            "Assisted-digital": {
                "channels": ["email", "sms", "phone"],
                "priority": "guided_digital", 
                "max_channels": 3
            },
            "Low/no-digital (offline-preferred)": {
                "channels": ["letter", "phone"],
                "priority": "traditional",
                "max_channels": 2
            },
            "Accessibility & alternate-format needs": {
                "channels": ["letter", "braille", "audio", "phone"],
                "priority": "accessible",
                "max_channels": 4
            },
            "Vulnerable / extra-support": {
                "channels": ["letter", "phone"],
                "priority": "supportive",
                "max_channels": 2
            }
        }
        
        # Communication type rules
        self.communication_type_rules = {
            "REGULATORY": {
                "mandatory_channels": ["letter"],  # Legal requirement
                "max_channels": 2,
                "tone": "formal"
            },
            "PROMOTIONAL": {
                "mandatory_channels": [],
                "max_channels": 4,
                "tone": "engaging"
            },
            "INFORMATION": {
                "mandatory_channels": [],
                "max_channels": 2, 
                "tone": "clear"
            }
        }
    
    def initialize_apis(self) -> bool:
        """Initialize API connections."""
        try:
            self.api_manager = APIManager()
            self.logger.info("API Manager initialized for batch planning")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize APIs: {e}")
            return False
    
    def create_batch_communication_plans(self, customer_categories: List[Dict], 
                                       letter_text: str, 
                                       letter_classification: Dict) -> Dict[str, Any]:
        """
        Create communication plans for a batch of customers.
        
        Args:
            customer_categories: List of categorized customers
            letter_text: The letter content to communicate
            letter_classification: Classification of the letter (REGULATORY/PROMOTIONAL/INFORMATION)
            
        Returns:
            Complete batch results with individual plans and cost analysis
        """
        self.logger.info(f"Creating communication plans for {len(customer_categories)} customers")
        
        if not self.initialize_apis():
            return {"error": "Failed to initialize APIs"}
        
        # Extract classification
        classification_type = letter_classification.get('classification', 'INFORMATION')
        
        # Create individual plans
        individual_plans = []
        
        for customer in customer_categories:
            customer_id = customer.get('customer_id', 'unknown')
            customer_category = customer.get('category', 'Digital-first self-serve')
            
            # Create communication plan for this customer
            plan = self._create_individual_plan(
                customer, customer_category, letter_text, classification_type
            )
            
            individual_plans.append({
                'customer_id': customer_id,
                'customer_name': customer.get('name', 'Unknown'),
                'customer_category': customer_category,
                'plan': plan
            })
        
        # Calculate cost comparison
        cost_analysis = self._calculate_batch_costs(individual_plans, len(customer_categories))
        
        # Generate batch summary
        batch_summary = self._generate_batch_summary(individual_plans, classification_type)
        
        return {
            'batch_metadata': {
                'total_customers': len(customer_categories),
                'letter_classification': classification_type,
                'generated_at': datetime.now().isoformat(),
                'cost_scenario': self.cost_manager.current_scenario
            },
            'individual_plans': individual_plans,
            'cost_analysis': cost_analysis,
            'batch_summary': batch_summary,
            'recommendations': self._generate_recommendations(cost_analysis, batch_summary)
        }
    
    def _create_individual_plan(self, customer: Dict, category: str, 
                              letter_text: str, classification: str) -> Dict[str, Any]:
        """Create communication plan for individual customer."""
        
        # Get strategy for this customer category
        strategy = self.category_strategies.get(category, self.category_strategies["Digital-first self-serve"])
        
        # Get classification rules
        type_rules = self.communication_type_rules.get(classification, {})
        
        # Build timeline based on category and classification
        timeline = self._build_communication_timeline(strategy, type_rules, category, classification)
        
        # Create mock communication result for business rules
        mock_result = {
            "customer_category": {"label": category},
            "classification": {"label": classification},
            "comms_plan": {"timeline": timeline},
            "assets": self._generate_mock_assets(timeline),
            "upsell_included": self._should_include_upsell(customer, classification),
            "upsell_details": self._generate_upsell_details(customer, classification)
        }
        
        # Apply business rules
        final_result = self.business_rules.apply_all_rules(mock_result, customer)
        
        # Calculate individual cost
        individual_cost = self._calculate_individual_cost(final_result.get("comms_plan", {}).get("timeline", []))
        
        return {
            'communication_strategy': final_result,
            'cost_breakdown': individual_cost,
            'personalization_notes': final_result.get('personalization_notes', [])
        }
    
    def _build_communication_timeline(self, strategy: Dict, type_rules: Dict, 
                                    category: str, classification: str) -> List[Dict]:
        """Build communication timeline based on strategy and rules."""
        
        timeline = []
        step = 1
        
        # Add mandatory channels first
        mandatory = type_rules.get('mandatory_channels', [])
        for channel in mandatory:
            timeline.append({
                'step': step,
                'channel': channel,
                'when': 'immediate',
                'purpose': f'Mandatory {classification.lower()} communication',
                'why': f'Required for {classification} compliance'
            })
            step += 1
        
        # Add strategy channels (avoiding duplicates)
        strategy_channels = strategy.get('channels', [])
        max_channels = min(type_rules.get('max_channels', 4), strategy.get('max_channels', 4))
        
        for channel in strategy_channels:
            if channel not in mandatory and len(timeline) < max_channels:
                timeline.append({
                    'step': step,
                    'channel': channel,
                    'when': self._get_channel_timing(channel, step),
                    'purpose': self._get_channel_purpose(channel, category, classification),
                    'why': self._get_channel_reasoning(channel, category)
                })
                step += 1
        
        return timeline
    
    def _get_channel_timing(self, channel: str, step: int) -> str:
        """Get appropriate timing for channel."""
        timing_map = {
            'in_app': 'immediate',
            'email': 'immediate', 
            'sms': '+1 hour',
            'letter': 'immediate',
            'phone': '+1 day',
            'voice_note': 'immediate',
            'braille': '+1 day',
            'audio': '+1 day'
        }
        return timing_map.get(channel, '+1 day')
    
    def _get_channel_purpose(self, channel: str, category: str, classification: str) -> str:
        """Get purpose description for channel."""
        purposes = {
            'in_app': f'{classification} notification for digital-first experience',
            'email': f'{classification} communication with full details',
            'sms': f'Quick {classification} alert and summary',
            'letter': f'Formal {classification} documentation',
            'phone': f'Personal support call for {classification} matter',
            'voice_note': f'Audio version for convenient {classification} access',
            'braille': f'Accessible {classification} format',
            'audio': f'Audio {classification} communication'
        }
        return purposes.get(channel, f'{classification} communication')
    
    def _get_channel_reasoning(self, channel: str, category: str) -> str:
        """Get reasoning for channel selection."""
        reasoning = {
            'in_app': f'{category} customers prefer app-based communication',
            'email': f'Suitable for {category} with digital capability',
            'sms': f'Quick reach for {category} customers',
            'letter': f'Preferred method for {category} customers',
            'phone': f'{category} customers benefit from personal contact',
            'voice_note': f'Audio convenience for {category} customers',
            'braille': f'Accessibility requirement for {category}',
            'audio': f'Alternative format for {category}'
        }
        return reasoning.get(channel, f'Appropriate for {category}')
    
    def _generate_mock_assets(self, timeline: List[Dict]) -> Dict[str, Any]:
        """Generate mock communication assets."""
        assets = {}
        
        for step in timeline:
            channel = step.get('channel', '')
            
            if channel == 'email':
                assets['email_html'] = {
                    'subject': 'Important Account Information',
                    'html': '<p>Email content would be generated here</p>'
                }
            elif channel == 'sms':
                assets['sms_text'] = 'SMS content would be generated here (max 160 chars)'
            elif channel == 'letter':
                assets['letter_docx_body'] = 'Letter content would be generated here'
            elif channel == 'in_app':
                assets['in_app_notification'] = 'In-app notification content here'
            elif channel == 'voice_note':
                assets['voice_note_text'] = 'Voice note script would be generated here'
            elif channel == 'braille':
                assets['braille_text_optional'] = 'Braille format content here'
        
        return assets
    
    def _should_include_upsell(self, customer: Dict, classification: str) -> bool:
        """Determine if upsell should be included."""
        # No upsell for regulatory
        if classification == 'REGULATORY':
            return False
        
        # No upsell for vulnerable customers
        if customer.get('category') == 'Vulnerable / extra-support':
            return False
        
        # Check if customer is upsell eligible
        return customer.get('upsell_eligible', False)
    
    def _generate_upsell_details(self, customer: Dict, classification: str) -> Dict[str, Any]:
        """Generate upsell details if applicable."""
        if not self._should_include_upsell(customer, classification):
            return {
                'product': None,
                'reasoning': 'No upsell appropriate for this customer/communication type',
                'message': None
            }
        
        # Mock upsell based on customer category
        category = customer.get('category', '')
        
        if 'Digital' in category:
            return {
                'product': 'Premium Digital Banking',
                'reasoning': 'Digital-savvy customer would benefit from premium features',
                'message': 'Upgrade to Premium Digital Banking for enhanced features'
            }
        else:
            return {
                'product': 'Premium Account',
                'reasoning': 'Customer profile suggests premium account suitability',
                'message': 'Consider our Premium Account for additional benefits'
            }
    
    def _calculate_individual_cost(self, timeline: List[Dict]) -> Dict[str, Any]:
        """Calculate cost for individual customer's timeline."""
        
        total_cost = 0
        total_carbon = 0
        channel_costs = {}
        
        for step in timeline:
            channel = step.get('channel', '')
            
            # Map to cost calculation channels
            cost_channel = self._map_channel_for_costing(channel)
            
            if cost_channel:
                calc = self.cost_manager.calculate_communication_cost(cost_channel, 1)
                total_cost += calc['total_cost']
                total_carbon += calc['total_carbon_kg']
                
                channel_costs[channel] = {
                    'cost': calc['total_cost'],
                    'carbon_kg': calc['total_carbon_kg']
                }
        
        return {
            'total_cost': total_cost,
            'total_carbon_kg': total_carbon,
            'channel_breakdown': channel_costs,
            'channels_used': len(timeline)
        }
    
    def _map_channel_for_costing(self, channel: str) -> Optional[str]:
        """Map timeline channels to cost calculation channels."""
        mapping = {
            'email': 'email',
            'sms': 'sms',
            'letter': 'letter', 
            'in_app': 'in_app',
            'voice_note': 'voice_note',
            'braille': 'letter',  # Similar cost to letter
            'audio': 'voice_note',  # Similar to voice note
            'phone': None  # No direct cost in our model
        }
        return mapping.get(channel.lower())
    
    def _calculate_batch_costs(self, individual_plans: List[Dict], total_customers: int) -> Dict[str, Any]:
        """Calculate batch cost analysis vs traditional approach."""
        
        # Calculate optimized approach costs
        optimized_total_cost = 0
        optimized_total_carbon = 0
        channel_usage = {}
        
        for plan_data in individual_plans:
            plan = plan_data['plan']
            cost_breakdown = plan['cost_breakdown']
            
            optimized_total_cost += cost_breakdown['total_cost']
            optimized_total_carbon += cost_breakdown['total_carbon_kg']
            
            # Track channel usage
            for channel, data in cost_breakdown['channel_breakdown'].items():
                if channel not in channel_usage:
                    channel_usage[channel] = {'customers': 0, 'total_cost': 0}
                channel_usage[channel]['customers'] += 1
                channel_usage[channel]['total_cost'] += data['cost']
        
        # Calculate traditional approach (everyone gets a letter)
        traditional_calc = self.cost_manager.calculate_communication_cost('letter', total_customers)
        traditional_total_cost = traditional_calc['total_cost']
        traditional_total_carbon = traditional_calc['total_carbon_kg']
        
        # Calculate savings
        cost_savings = traditional_total_cost - optimized_total_cost
        carbon_savings = traditional_total_carbon - optimized_total_carbon
        
        savings_percentage = (cost_savings / traditional_total_cost * 100) if traditional_total_cost > 0 else 0
        carbon_savings_percentage = (carbon_savings / traditional_total_carbon * 100) if traditional_total_carbon > 0 else 0
        
        return {
            'traditional_approach': {
                'description': 'Everyone gets a letter',
                'total_cost': traditional_total_cost,
                'total_carbon_kg': traditional_total_carbon,
                'cost_per_customer': traditional_total_cost / total_customers if total_customers > 0 else 0
            },
            'optimized_approach': {
                'description': 'Personalized communication strategy',
                'total_cost': optimized_total_cost,
                'total_carbon_kg': optimized_total_carbon,
                'cost_per_customer': optimized_total_cost / total_customers if total_customers > 0 else 0,
                'channel_usage': channel_usage
            },
            'savings': {
                'cost_savings': cost_savings,
                'cost_savings_percentage': savings_percentage,
                'carbon_savings_kg': carbon_savings,
                'carbon_savings_percentage': carbon_savings_percentage,
                'break_even_point': 'Immediate' if cost_savings > 0 else 'Not achieved'
            },
            'scenario_used': self.cost_manager.current_scenario
        }
    
    def _generate_batch_summary(self, individual_plans: List[Dict], classification: str) -> Dict[str, Any]:
        """Generate summary statistics for the batch."""
        
        # Count customers by category
        category_counts = {}
        channel_popularity = {}
        upsell_eligible_count = 0
        
        for plan_data in individual_plans:
            category = plan_data['customer_category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count channel usage
            timeline = plan_data['plan']['communication_strategy'].get('comms_plan', {}).get('timeline', [])
            for step in timeline:
                channel = step.get('channel', '')
                channel_popularity[channel] = channel_popularity.get(channel, 0) + 1
            
            # Count upsell eligible
            if plan_data['plan']['communication_strategy'].get('upsell_included', False):
                upsell_eligible_count += 1
        
        # Find most popular approach
        most_popular_channel = max(channel_popularity.items(), key=lambda x: x[1])[0] if channel_popularity else 'none'
        
        return {
            'total_customers_processed': len(individual_plans),
            'letter_classification': classification,
            'customer_distribution': category_counts,
            'channel_popularity': channel_popularity,
            'most_popular_channel': most_popular_channel,
            'upsell_opportunities': upsell_eligible_count,
            'average_channels_per_customer': sum(channel_popularity.values()) / len(individual_plans) if individual_plans else 0,
            'communication_efficiency': {
                'digital_percentage': sum(channel_popularity.get(ch, 0) for ch in ['email', 'in_app', 'sms', 'voice_note']) / sum(channel_popularity.values()) * 100 if channel_popularity else 0,
                'traditional_percentage': sum(channel_popularity.get(ch, 0) for ch in ['letter', 'phone']) / sum(channel_popularity.values()) * 100 if channel_popularity else 0
            }
        }
    
    def _generate_recommendations(self, cost_analysis: Dict, batch_summary: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        savings_pct = cost_analysis['savings']['cost_savings_percentage']
        carbon_savings_pct = cost_analysis['savings']['carbon_savings_percentage']
        
        # Cost savings recommendations
        if savings_pct > 70:
            recommendations.append(f"🎉 Excellent cost optimization! {savings_pct:.0f}% savings achieved through smart targeting.")
        elif savings_pct > 50:
            recommendations.append(f"✅ Good cost savings of {savings_pct:.0f}% achieved. Consider further digital adoption.")
        else:
            recommendations.append(f"⚠️ Limited savings of {savings_pct:.0f}%. Review customer segmentation strategy.")
        
        # Environmental impact
        if carbon_savings_pct > 70:
            recommendations.append(f"🌱 Significant environmental impact: {carbon_savings_pct:.0f}% carbon reduction!")
        
        # Channel efficiency
        digital_pct = batch_summary['communication_efficiency']['digital_percentage']
        if digital_pct > 70:
            recommendations.append(f"📱 High digital adoption ({digital_pct:.0f}%) - consider advanced digital features.")
        elif digital_pct < 30:
            recommendations.append(f"📮 High traditional communication usage - invest in digital education programs.")
        
        # Upsell opportunities
        upsell_rate = (batch_summary['upsell_opportunities'] / batch_summary['total_customers_processed'] * 100) if batch_summary['total_customers_processed'] > 0 else 0
        if upsell_rate > 40:
            recommendations.append(f"💎 Strong upsell potential ({upsell_rate:.0f}% of customers) - prioritize sales follow-up.")
        elif upsell_rate < 10:
            recommendations.append(f"🛡️ Low upsell rate ({upsell_rate:.0f}%) indicates good vulnerable customer protection.")
        
        # Channel optimization
        most_popular = batch_summary['most_popular_channel']
        if most_popular == 'letter':
            recommendations.append("📮 Letter-heavy approach detected - consider digital coaching programs.")
        elif most_popular in ['email', 'in_app']:
            recommendations.append(f"✅ {most_popular.title()}-first approach working well - maintain digital strategy.")
        
        return recommendations

def demo_batch_planner():
    """Demonstrate the batch communication planner."""
    print("🚀 Batch Communication Planner Demo")
    print("=" * 50)
    
    # Sample customer categories
    sample_customers = [
        {
            'customer_id': 'CUST001',
            'name': 'Digital Dave',
            'category': 'Digital-first self-serve',
            'upsell_eligible': True
        },
        {
            'customer_id': 'CUST002', 
            'name': 'Vulnerable Vera',
            'category': 'Vulnerable / extra-support',
            'upsell_eligible': False
        },
        {
            'customer_id': 'CUST003',
            'name': 'Offline Oliver',
            'category': 'Low/no-digital (offline-preferred)',
            'upsell_eligible': True
        }
    ]
    
    # Sample letter classification
    letter_classification = {
        'classification': 'INFORMATION',
        'confidence': 8,
        'reasoning': 'Account update notification'
    }
    
    # Create planner and generate plans
    planner = BatchCommunicationPlanner()
    
    results = planner.create_batch_communication_plans(
        sample_customers,
        "Sample letter content about account updates...",
        letter_classification
    )
    
    # Display results
    print(f"\n📊 Batch Results:")
    print(f"Customers processed: {results['batch_metadata']['total_customers']}")
    print(f"Letter type: {results['batch_metadata']['letter_classification']}")
    
    cost_analysis = results['cost_analysis']
    print(f"\n💰 Cost Analysis:")
    print(f"Traditional cost: £{cost_analysis['traditional_approach']['total_cost']:.2f}")
    print(f"Optimized cost: £{cost_analysis['optimized_approach']['total_cost']:.2f}")
    print(f"Savings: £{cost_analysis['savings']['cost_savings']:.2f} ({cost_analysis['savings']['cost_savings_percentage']:.0f}%)")
    
    print(f"\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"  {rec}")

if __name__ == "__main__":
    demo_batch_planner()