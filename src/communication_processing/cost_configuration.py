"""
Communication Cost Configuration System
Configurable cost assumptions for different communication channels and scenarios.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CommunicationCosts:
    """Cost structure for different communication channels."""
    # Physical channels
    letter_postage: float = 0.85  # More realistic UK 2nd class stamp
    letter_printing: float = 0.08  # Basic printing cost
    letter_envelope: float = 0.03  # Envelope cost
    letter_staff_time: float = 0.50  # 2 minutes @ £15/hour = realistic
    
    # Digital channels  
    email_cost: float = 0.002
    sms_cost: float = 0.05
    in_app_notification: float = 0.001
    voice_note_generation: float = 0.02
    
    # Environmental impact (CO2g per communication)
    letter_carbon_g: float = 25.0
    email_carbon_g: float = 0.3
    sms_carbon_g: float = 0.1
    in_app_carbon_g: float = 0.05
    
    # Staff time (minutes per communication type)
    letter_staff_minutes: float = 2.0
    email_staff_minutes: float = 0.1
    sms_staff_minutes: float = 0.05
    
    # Staff hourly rate for calculations
    staff_hourly_rate: float = 15.0

@dataclass
class VolumeDiscounts:
    """Volume-based discounts for bulk communications."""
    small_volume_threshold: int = 100
    medium_volume_threshold: int = 1000
    large_volume_threshold: int = 5000
    
    small_discount: float = 0.0
    medium_discount: float = 0.05  # 5% discount
    large_discount: float = 0.15   # 15% discount

@dataclass
class ScenarioAssumptions:
    """Different cost scenarios for sensitivity analysis."""
    name: str
    costs: CommunicationCosts
    discounts: VolumeDiscounts
    description: str

class CostConfigurationManager:
    """Manages cost assumptions and scenarios."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize cost configuration manager."""
        self.logger = logging.getLogger(__name__)
        
        if config_dir is None:
            config_dir = Path("data/cost_config")
        
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default scenarios
        self.scenarios = self._create_default_scenarios()
        self.current_scenario = "realistic"
        
        # Load or create config file
        self.config_file = self.config_dir / "cost_assumptions.json"
        self._load_or_create_config()
    
    def _create_default_scenarios(self) -> Dict[str, ScenarioAssumptions]:
        """Create default cost scenarios."""
        
        # Realistic scenario (base case)
        realistic_costs = CommunicationCosts(
            letter_postage=0.85,
            letter_printing=0.08,
            letter_envelope=0.03,
            letter_staff_time=0.50,  # 2 mins at £15/hour
            email_cost=0.002,
            sms_cost=0.05,
            in_app_notification=0.001,
            voice_note_generation=0.02
        )
        
        # Conservative scenario (higher costs)
        conservative_costs = CommunicationCosts(
            letter_postage=1.20,
            letter_printing=0.15,
            letter_envelope=0.05,
            letter_staff_time=1.25,  # 5 mins at £15/hour
            email_cost=0.005,
            sms_cost=0.08,
            in_app_notification=0.003,
            voice_note_generation=0.035
        )
        
        # Optimistic scenario (lower costs, good automation)
        optimistic_costs = CommunicationCosts(
            letter_postage=0.65,  # Bulk discount
            letter_printing=0.04,
            letter_envelope=0.02,
            letter_staff_time=0.25,  # 1 min with automation
            email_cost=0.001,
            sms_cost=0.03,
            in_app_notification=0.0005,
            voice_note_generation=0.015
        )
        
        # Standard volume discounts
        standard_discounts = VolumeDiscounts()
        
        return {
            "realistic": ScenarioAssumptions(
                name="Realistic",
                costs=realistic_costs,
                discounts=standard_discounts,
                description="Realistic costs based on current UK market rates"
            ),
            "conservative": ScenarioAssumptions(
                name="Conservative",
                costs=conservative_costs,
                discounts=standard_discounts,
                description="Higher costs for worst-case planning"
            ),
            "optimistic": ScenarioAssumptions(
                name="Optimistic",
                costs=optimistic_costs,
                discounts=standard_discounts,
                description="Lower costs with automation and bulk discounts"
            )
        }
    
    def _load_or_create_config(self):
        """Load existing config or create new one."""
        if self.config_file.exists():
            try:
                self._load_config()
                self.logger.info("Loaded existing cost configuration")
            except Exception as e:
                self.logger.warning(f"Error loading config: {e}, using defaults")
                self._save_config()
        else:
            self._save_config()
            self.logger.info("Created new cost configuration file")
    
    def _load_config(self):
        """Load configuration from JSON file."""
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
        self.current_scenario = data.get("current_scenario", "realistic")
        
        # Load scenarios
        scenarios_data = data.get("scenarios", {})
        for name, scenario_data in scenarios_data.items():
            costs_data = scenario_data["costs"]
            discounts_data = scenario_data["discounts"]
            
            costs = CommunicationCosts(**costs_data)
            discounts = VolumeDiscounts(**discounts_data)
            
            self.scenarios[name] = ScenarioAssumptions(
                name=scenario_data["name"],
                costs=costs,
                discounts=discounts,
                description=scenario_data["description"]
            )
    
    def _save_config(self):
        """Save configuration to JSON file."""
        data = {
            "last_updated": datetime.now().isoformat(),
            "current_scenario": self.current_scenario,
            "scenarios": {}
        }
        
        for name, scenario in self.scenarios.items():
            data["scenarios"][name] = {
                "name": scenario.name,
                "description": scenario.description,
                "costs": asdict(scenario.costs),
                "discounts": asdict(scenario.discounts)
            }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_current_costs(self) -> CommunicationCosts:
        """Get costs for current scenario."""
        return self.scenarios[self.current_scenario].costs
    
    def get_current_discounts(self) -> VolumeDiscounts:
        """Get volume discounts for current scenario."""
        return self.scenarios[self.current_scenario].discounts
    
    def set_scenario(self, scenario_name: str):
        """Switch to different cost scenario."""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        self.current_scenario = scenario_name
        self._save_config()
        self.logger.info(f"Switched to scenario: {scenario_name}")
    
    def calculate_communication_cost(self, channel: str, volume: int = 1) -> Dict[str, float]:
        """Calculate cost for a communication channel."""
        costs = self.get_current_costs()
        discounts = self.get_current_discounts()
        
        # Base costs per channel
        base_costs = {
            "letter": (costs.letter_postage + costs.letter_printing + 
                      costs.letter_envelope + costs.letter_staff_time),
            "email": costs.email_cost + (costs.email_staff_minutes / 60 * costs.staff_hourly_rate),
            "sms": costs.sms_cost + (costs.sms_staff_minutes / 60 * costs.staff_hourly_rate),
            "in_app": costs.in_app_notification,
            "voice_note": costs.voice_note_generation
        }
        
        if channel not in base_costs:
            raise ValueError(f"Unknown channel: {channel}")
        
        base_cost = base_costs[channel]
        
        # Apply volume discounts
        discount = 0.0
        if volume >= discounts.large_volume_threshold:
            discount = discounts.large_discount
        elif volume >= discounts.medium_volume_threshold:
            discount = discounts.medium_discount
        elif volume >= discounts.small_volume_threshold:
            discount = discounts.small_discount
        
        discounted_cost = base_cost * (1 - discount)
        total_cost = discounted_cost * volume
        
        # Environmental impact
        carbon_per_item = {
            "letter": costs.letter_carbon_g,
            "email": costs.email_carbon_g,
            "sms": costs.sms_carbon_g,
            "in_app": costs.in_app_carbon_g,
            "voice_note": costs.email_carbon_g  # Similar to email
        }
        
        total_carbon = carbon_per_item.get(channel, 0) * volume
        
        return {
            "channel": channel,
            "volume": volume,
            "cost_per_item": base_cost,
            "discount_applied": discount,
            "discounted_cost_per_item": discounted_cost,
            "total_cost": total_cost,
            "total_carbon_g": total_carbon,
            "total_carbon_kg": total_carbon / 1000
        }