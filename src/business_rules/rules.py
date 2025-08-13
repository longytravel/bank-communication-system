"""
Business Rules Configuration
Central place to enable/disable and configure business rules.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class RuleConfig:
    """Configuration for a single business rule."""
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    description: str = ""
    applies_to: List[str] = None  # Customer categories or communication types this rule applies to

class BusinessRulesConfig:
    """
    Central configuration for all business rules.
    Easy to modify rules without changing core logic.
    """
    
    def __init__(self):
        """Initialize with default rule configurations."""
        
        # Customer Category Rules
        self.customer_rules = {
            "digital_first_in_app_only": RuleConfig(
                enabled=True,
                priority=1,
                description="Digital-first customers get in-app notifications only, no phone scripts",
                applies_to=["Digital-first self-serve"]
            ),
            
            "digital_first_voice_notes": RuleConfig(
                enabled=True,
                priority=2,
                description="Add voice notes for digital-first customers for convenience",
                applies_to=["Digital-first self-serve"]
            ),
            
            "assisted_digital_coaching": RuleConfig(
                enabled=True,
                priority=3,
                description="Offer coaching calls to help with digital adoption",
                applies_to=["Assisted-digital"]
            ),
            
            "low_digital_coaching": RuleConfig(
                enabled=True,
                priority=3,
                description="Offer gentle coaching calls for digital onboarding",
                applies_to=["Low/no-digital (offline-preferred)"]
            ),
            
            "low_digital_postal_first": RuleConfig(
                enabled=True,
                priority=1,
                description="Ensure postal delivery for offline-preferred customers",
                applies_to=["Low/no-digital (offline-preferred)"]
            ),
            
            "vulnerable_callback_support": RuleConfig(
                enabled=True,
                priority=1,
                description="Add proactive callback offers for vulnerable customers",
                applies_to=["Vulnerable / extra-support"]
            ),
            
            "accessibility_multiple_formats": RuleConfig(
                enabled=True,
                priority=1,
                description="Ensure braille and audio formats for accessibility needs",
                applies_to=["Accessibility & alternate-format needs"]
            )
        }
        
        # Communication Type Rules
        self.communication_rules = {
            "regulatory_mandatory_postal": RuleConfig(
                enabled=True,
                priority=1,
                description="MANDATORY: Postal delivery required for regulatory communications",
                applies_to=["REGULATORY"]
            ),
            
            "regulatory_formal_tone": RuleConfig(
                enabled=True,
                priority=2,
                description="Ensure formal tone for all regulatory communications",
                applies_to=["REGULATORY"]
            ),
            
            "promotional_vulnerable_block": RuleConfig(
                enabled=True,
                priority=1,
                description="CRITICAL: Block all promotional content for vulnerable customers",
                applies_to=["PROMOTIONAL"]
            ),
            
            "promotional_enhanced_materials": RuleConfig(
                enabled=True,
                priority=3,
                description="Enhance promotional materials for eligible customers",
                applies_to=["PROMOTIONAL"]
            ),
            
            "information_clarity_optimization": RuleConfig(
                enabled=True,
                priority=2,
                description="Optimize informational content for clarity and accessibility",
                applies_to=["INFORMATION"]
            )
        }
        
        # Critical Protection Rules (CANNOT be disabled)
        self.protection_rules = {
            "vulnerable_sales_removal": RuleConfig(
                enabled=True,
                priority=1,
                description="CRITICAL: Remove ALL sales/promotional content for vulnerable customers",
                applies_to=["Vulnerable / extra-support"]
            ),
            
            "regulatory_compliance_override": RuleConfig(
                enabled=True,
                priority=1,
                description="CRITICAL: Ensure regulatory compliance overrides all other rules",
                applies_to=["REGULATORY"]
            )
        }
    
    def is_rule_enabled(self, rule_category: str, rule_name: str) -> bool:
        """Check if a specific rule is enabled."""
        if rule_category == "customer":
            return self.customer_rules.get(rule_name, RuleConfig()).enabled
        elif rule_category == "communication":
            return self.communication_rules.get(rule_name, RuleConfig()).enabled
        elif rule_category == "protection":
            # Protection rules are ALWAYS enabled for safety
            return True
        return False
    
    def get_rule_config(self, rule_category: str, rule_name: str) -> RuleConfig:
        """Get configuration for a specific rule."""
        if rule_category == "customer":
            return self.customer_rules.get(rule_name, RuleConfig())
        elif rule_category == "communication":
            return self.communication_rules.get(rule_name, RuleConfig())
        elif rule_category == "protection":
            return self.protection_rules.get(rule_name, RuleConfig())
        return RuleConfig(enabled=False)
    
    def get_rules_for_customer_category(self, category: str) -> List[str]:
        """Get all enabled rules that apply to a customer category."""
        applicable_rules = []
        
        for rule_name, config in self.customer_rules.items():
            if config.enabled and config.applies_to and category in config.applies_to:
                applicable_rules.append(rule_name)
        
        # Always include protection rules for vulnerable customers
        if category == "Vulnerable / extra-support":
            applicable_rules.extend(self.protection_rules.keys())
        
        return applicable_rules
    
    def get_rules_for_communication_type(self, comm_type: str) -> List[str]:
        """Get all enabled rules that apply to a communication type."""
        applicable_rules = []
        
        for rule_name, config in self.communication_rules.items():
            if config.enabled and config.applies_to and comm_type in config.applies_to:
                applicable_rules.append(rule_name)
        
        # Always include protection rules for regulatory
        if comm_type == "REGULATORY":
            applicable_rules.extend([r for r in self.protection_rules.keys() 
                                   if "regulatory" in r])
        
        return applicable_rules
    
    def disable_rule(self, rule_category: str, rule_name: str) -> bool:
        """
        Disable a rule (if allowed).
        Protection rules cannot be disabled.
        """
        if rule_category == "protection":
            return False  # Cannot disable protection rules
        
        if rule_category == "customer" and rule_name in self.customer_rules:
            self.customer_rules[rule_name].enabled = False
            return True
        elif rule_category == "communication" and rule_name in self.communication_rules:
            self.communication_rules[rule_name].enabled = False
            return True
        
        return False
    
    def enable_rule(self, rule_category: str, rule_name: str) -> bool:
        """Enable a rule."""
        if rule_category == "customer" and rule_name in self.customer_rules:
            self.customer_rules[rule_name].enabled = True
            return True
        elif rule_category == "communication" and rule_name in self.communication_rules:
            self.communication_rules[rule_name].enabled = True
            return True
        
        return False
    
    def get_all_rules_summary(self) -> Dict[str, Any]:
        """Get a summary of all rules for documentation/debugging."""
        return {
            "customer_rules": {
                name: {
                    "enabled": config.enabled,
                    "priority": config.priority,
                    "description": config.description,
                    "applies_to": config.applies_to
                }
                for name, config in self.customer_rules.items()
            },
            "communication_rules": {
                name: {
                    "enabled": config.enabled,
                    "priority": config.priority,
                    "description": config.description,
                    "applies_to": config.applies_to
                }
                for name, config in self.communication_rules.items()
            },
            "protection_rules": {
                name: {
                    "enabled": True,  # Always enabled
                    "priority": config.priority,
                    "description": config.description,
                    "applies_to": config.applies_to
                }
                for name, config in self.protection_rules.items()
            }
        }

# Global configuration instance
rules_config = BusinessRulesConfig()

# Convenience functions
def is_rule_enabled(rule_category: str, rule_name: str) -> bool:
    """Check if a rule is enabled."""
    return rules_config.is_rule_enabled(rule_category, rule_name)

def get_customer_rules(category: str) -> List[str]:
    """Get rules for a customer category."""
    return rules_config.get_rules_for_customer_category(category)

def get_communication_rules(comm_type: str) -> List[str]:
    """Get rules for a communication type."""
    return rules_config.get_rules_for_communication_type(comm_type)