"""
Business Rules Engine
Applies modular business rules to communication strategies.
"""

import logging
from typing import Dict, Any, List
from .customer_rules import CustomerCategoryRules
from .communication_rules import CommunicationRules
from .video_rules import VideoEligibilityRules

class BusinessRulesEngine:
    """
    Main engine that orchestrates all business rules.
    Rules are modular and can be easily added/removed.
    """
    
    def __init__(self):
        """Initialize the rules engine with all rule modules."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize rule modules
        self.customer_rules = CustomerCategoryRules()
        self.communication_rules = CommunicationRules()
        self.video_rules = VideoEligibilityRules()
        
        # Track applied rules for debugging
        self.applied_rules = []
        
        self.logger.info("Business Rules Engine initialized with video support")
    
    def apply_all_rules(self, result: Dict[str, Any], customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all business rules to a communication strategy.
        
        Args:
            result: The communication strategy result
            customer_profile: Full customer profile data
            
        Returns:
            Modified result with all rules applied
        """
        self.applied_rules = []  # Reset for this run
        
        customer_category = result.get("customer_category", {}).get("label", "")
        classification = result.get("classification", {}).get("label", "")
        
        self.logger.info(f"Applying rules for category: {customer_category}, classification: {classification}")
        
        # Apply customer category rules
        result = self.customer_rules.apply_category_rules(result, customer_category, customer_profile)
        
        # Apply communication rules  
        result = self.communication_rules.apply_communication_rules(result, classification)
        
        # NEW: Apply video eligibility rules
        result = self.video_rules.apply_video_rules(result, customer_profile)
        if result.get('video_eligible'):
            self.applied_rules.append("VIDEO_ELIGIBILITY")
        
        # Apply overrides and final validations
        result = self._apply_final_validations(result, customer_profile)
        
        # Log what rules were applied
        self._log_applied_rules(result)
        
        return result
    
    def _apply_final_validations(self, result: Dict[str, Any], customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply final validation rules that override everything else."""
        
        # CRITICAL: Vulnerable customer protection override
        customer_category = result.get("customer_category", {}).get("label", "")
        if customer_category == "Vulnerable / extra-support":
            result = self._apply_vulnerable_protection(result)
            result = self._remove_video_for_vulnerable(result)
        
        # Ensure regulatory compliance
        classification = result.get("classification", {}).get("label", "")
        if classification == "REGULATORY":
            result = self._ensure_regulatory_compliance(result)
            result = self._remove_video_for_regulatory(result)
        
        return result
    
    def _apply_vulnerable_protection(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """CRITICAL: Remove all sales content for vulnerable customers."""
        self.applied_rules.append("VULNERABLE_PROTECTION_OVERRIDE")
        
        # Force remove upsell
        result["upsell_included"] = False
        result["upsell_details"] = {
            "product": None,
            "reasoning": "Removed for vulnerable customer protection",
            "message": None,
            "cta": None
        }
        
        # Clean assets of sales content
        if "assets" in result:
            assets = result["assets"]
            
            # Clean email HTML
            if "email_html" in assets and isinstance(assets["email_html"], dict):
                html = assets["email_html"].get("html", "")
                # Remove promotional divs
                import re
                html = re.sub(r'<div[^>]*background:\s*#f0f8ff.*?</div>', '', html, flags=re.DOTALL)
                html = re.sub(r'💎.*?</div>', '', html, flags=re.DOTALL)
                assets["email_html"]["html"] = html
            
            # Clean other assets
            for asset_key in ["in_app_notification", "sms_text"]:
                if asset_key in assets:
                    content = str(assets[asset_key])
                    if any(word in content.lower() for word in ["offer", "upgrade", "exclusive", "💎"]):
                        assets[asset_key] = "We're here to help with your banking needs. Contact us for support."[:160 if asset_key == "sms_text" else 500]
        
        # Add protection note
        if "comms_plan" not in result:
            result["comms_plan"] = {}
        if "overrides_or_risks" not in result["comms_plan"]:
            result["comms_plan"]["overrides_or_risks"] = []
        
        result["comms_plan"]["overrides_or_risks"].insert(0,
            "⚠️ VULNERABLE CUSTOMER PROTECTION: All sales/promotional content removed")
        
        return result
    
    def _remove_video_for_vulnerable(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Remove video channel for vulnerable customers."""
        if 'comms_plan' in result and 'timeline' in result['comms_plan']:
            timeline = result['comms_plan']['timeline']
            # Remove video steps
            timeline = [step for step in timeline if step.get('channel') != 'video_message']
            # Renumber steps
            for i, step in enumerate(timeline, start=1):
                step['step'] = i
            result['comms_plan']['timeline'] = timeline
        
        # Remove video from assets
        if 'assets' in result and 'video_message' in result['assets']:
            del result['assets']['video_message']
        
        # Update video eligibility
        result['video_eligible'] = False
        result['video_ineligible_reasons'] = ['Vulnerable customer protection']
        
        return result
    
    def _remove_video_for_regulatory(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Remove video channel for regulatory communications."""
        if 'comms_plan' in result and 'timeline' in result['comms_plan']:
            timeline = result['comms_plan']['timeline']
            has_video = any(step.get('channel') == 'video_message' for step in timeline)
            
            if has_video:
                # Remove video steps
                timeline = [step for step in timeline if step.get('channel') != 'video_message']
                # Renumber steps
                for i, step in enumerate(timeline, start=1):
                    step['step'] = i
                result['comms_plan']['timeline'] = timeline
                
                # Add note
                if 'overrides_or_risks' not in result.get('comms_plan', {}):
                    result.setdefault('comms_plan', {})['overrides_or_risks'] = []
                result['comms_plan']['overrides_or_risks'].append(
                    "📋 Video removed for regulatory communication (durable medium required)"
                )
        
        # Remove video from assets
        if 'assets' in result and 'video_message' in result['assets']:
            del result['assets']['video_message']
        
        # Update video eligibility
        if result.get('video_eligible'):
            result['video_eligible'] = False
            result['video_ineligible_reasons'] = ['Regulatory communication requires durable medium']
        
        return result
    
    def _ensure_regulatory_compliance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure regulatory messages have proper durable medium delivery."""
        self.applied_rules.append("REGULATORY_COMPLIANCE_OVERRIDE")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        customer_category = result.get("customer_category", {}).get("label", "")
        
        # Determine required durable medium based on customer type
        if customer_category in ["Digital-first self-serve", "Assisted-digital"]:
            durable_channels = ["email", "in_app", "letter"]
            preferred_channel = "email"
        else:
            durable_channels = ["letter"]
            preferred_channel = "letter"
        
        # Ensure durable medium exists
        has_durable = any(
            str(step.get("channel", "")).lower() in durable_channels 
            for step in timeline
        )
        
        if not has_durable:
            timeline.insert(0, {
                "step": 1,
                "channel": preferred_channel,
                "when": "immediate", 
                "purpose": f"✅ REGULATORY COMPLIANCE - Durable medium via {preferred_channel}",
                "why": f"Legal requirement met via {preferred_channel}"
            })
            
            # Renumber remaining steps
            for i, step in enumerate(timeline[1:], start=2):
                step["step"] = i
        
        # Add compliance note
        if "comms_plan" not in result:
            result["comms_plan"] = {}
        if "overrides_or_risks" not in result["comms_plan"]:
            result["comms_plan"]["overrides_or_risks"] = []
        
        result["comms_plan"]["overrides_or_risks"].insert(0,
            f"✅ REGULATORY COMPLIANCE: Durable medium requirement satisfied via {preferred_channel}")
        
        result["comms_plan"]["timeline"] = timeline
        return result
    
    def _log_applied_rules(self, result: Dict[str, Any]):
        """Log which rules were applied for debugging."""
        if self.applied_rules:
            self.logger.info(f"Applied rules: {', '.join(self.applied_rules)}")
            
            # Add to result for transparency
            if "personalization_notes" not in result:
                result["personalization_notes"] = []
            
            result["personalization_notes"].append(f"Business rules applied: {', '.join(self.applied_rules)}")
    
    def get_active_rules(self) -> List[str]:
        """Get list of all active rule modules."""
        return [
            "CustomerCategoryRules",
            "CommunicationRules", 
            "VideoEligibilityRules",
            "VulnerableProtection",
            "RegulatoryCompliance"
        ]
    
    def get_rules_summary(self) -> Dict[str, str]:
        """Get summary of all rules for documentation."""
        return {
            "Digital-first customers": "Email as durable medium for regulatory, voice notes added",
            "High-value digital customers": "🎬 Personalized video messages for £10k+ balances",
            "Assisted-digital customers": "Email as durable medium, coaching calls offered",
            "Low/no-digital customers": "Letters for regulatory, coaching calls offered",
            "Vulnerable customers": "⚠️ Letters for regulatory, ALL sales content removed, no videos",
            "Accessibility needs": "Letters for regulatory, braille/audio formats ensured",
            "Regulatory communications": "✅ Email for digital customers, letters for traditional, no videos",
            "Upsell eligible": "Enhanced upsell materials generated, video for high-value customers"
        }
    
    def get_video_eligibility_stats(self, customers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get video eligibility statistics for customer base."""
        return self.video_rules.get_video_statistics(customers)