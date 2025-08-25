"""
Channel Limit Rules
Intelligently limits the number of communication channels to avoid overwhelming customers.
Configurable limits based on communication type and customer needs.
"""

import logging
from typing import Dict, Any, List

class ChannelLimitRules:
    """Rules for limiting communication channels to reasonable numbers."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # CONFIGURABLE LIMITS - Easy to change in future!
        self.channel_limits = {
            "REGULATORY": {
                "max_channels": 2,
                "reason": "Regulatory requires durable medium + 1 reminder max",
                "priority_order": ["letter", "email", "sms", "in_app"]  # Legal priority
            },
            "INFORMATION": {
                "max_channels": 3,
                "reason": "Information needs balanced reach without overwhelming",
                "priority_order": ["in_app", "email", "sms", "letter", "voice_note"]
            },
            "PROMOTIONAL": {
                "max_channels": 4,
                "reason": "Promotional can use more touchpoints for engagement",
                "priority_order": ["video_message", "in_app", "email", "sms", "voice_note", "letter"]
            },
            "DEFAULT": {
                "max_channels": 3,
                "reason": "Default limit to avoid overwhelming customers",
                "priority_order": ["email", "in_app", "sms", "letter"]
            }
        }
        
        # Customer category preferences (which channels work best)
        self.customer_preferences = {
            "Digital-first self-serve": {
                "preferred": ["video_message", "in_app", "email", "voice_note"],
                "avoid": ["letter", "phone"]
            },
            "Assisted-digital": {
                "preferred": ["email", "sms", "in_app"],
                "avoid": ["letter"]
            },
            "Low/no-digital (offline-preferred)": {
                "preferred": ["letter", "phone"],
                "avoid": ["in_app", "video_message", "voice_note"]
            },
            "Accessibility & alternate-format needs": {
                "preferred": ["letter", "voice_note", "email"],
                "avoid": ["video_message"]  # May not be accessible
            },
            "Vulnerable / extra-support": {
                "preferred": ["letter", "phone"],
                "avoid": ["video_message", "in_app"]  # Too complex
            }
        }
    
    def apply_channel_limits(self, result: Dict[str, Any], customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply intelligent channel limits to avoid overwhelming customers.
        
        Args:
            result: The communication strategy result
            customer_profile: Customer data
            
        Returns:
            Modified result with limited channels
        """
        timeline = result.get("comms_plan", {}).get("timeline", [])
        if not timeline:
            return result
        
        # Get communication type and customer category
        classification = result.get("classification", {}).get("label", "DEFAULT")
        customer_category = result.get("customer_category", {}).get("label", "")
        
        # Get the limit configuration
        limit_config = self.channel_limits.get(classification, self.channel_limits["DEFAULT"])
        max_channels = limit_config["max_channels"]
        
        # Get current channels
        current_channels = [step.get("channel") for step in timeline if step.get("channel")]
        unique_channels = list(dict.fromkeys(current_channels))  # Remove duplicates, preserve order
        
        self.logger.info(f"Current channels ({len(unique_channels)}): {unique_channels}")
        
        # If already within limit, return as is
        if len(unique_channels) <= max_channels:
            self.logger.info(f"Within limit of {max_channels}, no changes needed")
            return result
        
        # Need to reduce channels - pick the best ones
        selected_channels = self._select_best_channels(
            unique_channels,
            max_channels,
            classification,
            customer_category,
            customer_profile
        )
        
        self.logger.info(f"Selected best {max_channels} channels: {selected_channels}")
        
        # Filter timeline to only include selected channels
        new_timeline = []
        for step in timeline:
            if step.get("channel") in selected_channels:
                new_timeline.append(step)
        
        # Renumber steps
        for i, step in enumerate(new_timeline, start=1):
            step["step"] = i
        
        # Update the result
        result["comms_plan"]["timeline"] = new_timeline
        
        # Add note about optimization
        if "overrides_or_risks" not in result["comms_plan"]:
            result["comms_plan"]["overrides_or_risks"] = []
        
        removed_channels = [ch for ch in unique_channels if ch not in selected_channels]
        result["comms_plan"]["overrides_or_risks"].append(
            f"📊 CHANNEL OPTIMIZATION: Limited to {max_channels} channels for {classification}. "
            f"Removed: {', '.join(removed_channels)}"
        )
        
        # Update personalization notes
        if "personalization_notes" not in result:
            result["personalization_notes"] = []
        
        result["personalization_notes"].append(
            f"Optimized to {max_channels} channels to avoid overwhelming customer"
        )
        
        return result
    
    def _select_best_channels(self, channels: List[str], max_channels: int, 
                              classification: str, customer_category: str,
                              customer_profile: Dict[str, Any]) -> List[str]:
        """
        Intelligently select the best channels for this customer.
        
        Priority logic:
        1. Required channels (e.g., letter for regulatory if traditional customer)
        2. Customer preferred channels
        3. Most cost-effective channels
        4. Classification priority order
        """
        selected = []
        
        # Step 1: Add REQUIRED channels first
        required = self._get_required_channels(classification, customer_category)
        for channel in required:
            if channel in channels and channel not in selected:
                selected.append(channel)
                if len(selected) >= max_channels:
                    return selected
        
        # Step 2: Add customer PREFERRED channels
        preferences = self.customer_preferences.get(customer_category, {})
        preferred_channels = preferences.get("preferred", [])
        
        for channel in channels:
            if channel in preferred_channels and channel not in selected:
                selected.append(channel)
                if len(selected) >= max_channels:
                    return selected
        
        # Step 3: Add based on classification priority
        priority_order = self.channel_limits.get(classification, self.channel_limits["DEFAULT"])["priority_order"]
        
        for channel in priority_order:
            if channel in channels and channel not in selected:
                selected.append(channel)
                if len(selected) >= max_channels:
                    return selected
        
        # Step 4: Add any remaining channels (shouldn't happen)
        for channel in channels:
            if channel not in selected:
                selected.append(channel)
                if len(selected) >= max_channels:
                    return selected
        
        return selected
    
    def _get_required_channels(self, classification: str, customer_category: str) -> List[str]:
        """
        Get absolutely required channels that must be included.
        """
        required = []
        
        # Regulatory MUST have durable medium
        if classification == "REGULATORY":
            if customer_category in ["Digital-first self-serve", "Assisted-digital"]:
                required.append("email")  # Email is durable medium for digital
            else:
                required.append("letter")  # Letter for traditional/vulnerable
        
        # Vulnerable customers should always get letter for important comms
        if customer_category == "Vulnerable / extra-support":
            if classification in ["REGULATORY", "INFORMATION"]:
                if "letter" not in required:
                    required.append("letter")
        
        return required
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration for display/editing.
        """
        return {
            "channel_limits": self.channel_limits,
            "customer_preferences": self.customer_preferences
        }
    
    def update_limits(self, classification: str, new_limit: int):
        """
        Update the channel limit for a classification type.
        
        Args:
            classification: REGULATORY, INFORMATION, or PROMOTIONAL
            new_limit: New maximum number of channels
        """
        if classification in self.channel_limits:
            old_limit = self.channel_limits[classification]["max_channels"]
            self.channel_limits[classification]["max_channels"] = new_limit
            self.logger.info(f"Updated {classification} limit from {old_limit} to {new_limit}")
            return True
        return False