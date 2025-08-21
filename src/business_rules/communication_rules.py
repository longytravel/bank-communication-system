"""
Communication Rules
Rules specific to different types of communications (regulatory, promotional, etc.).
"""

import logging
from typing import Dict, Any

class CommunicationRules:
    """Rules that apply based on communication type/classification."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def apply_communication_rules(self, result: Dict[str, Any], classification: str) -> Dict[str, Any]:
        """Apply rules based on communication classification."""
        
        if classification == "REGULATORY":
            result = self._apply_regulatory_rules(result)
        
        elif classification == "PROMOTIONAL":
            result = self._apply_promotional_rules(result)
        
        elif classification == "INFORMATION":
            result = self._apply_information_rules(result)
        
        return result
    
    def _apply_regulatory_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for regulatory communications - DURABLE MEDIUM compliance."""
        self.logger.info("Applying regulatory communication rules")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        customer_category = result.get("customer_category", {}).get("label", "")
        
        # Define durable medium channels based on customer type
        if customer_category == "Digital-first self-serve":
            # For digital customers, email IS a durable medium
            durable_channels = ["email", "in_app", "letter"]
            preferred_durable = "email"  # Prefer email over letter
        elif customer_category == "Assisted-digital":
            # For assisted-digital, email can also be durable medium
            durable_channels = ["email", "letter"]
            preferred_durable = "email"
        else:
            # For traditional/vulnerable customers, stick with letter
            durable_channels = ["letter"]
            preferred_durable = "letter"
        
        # Check if we have at least one durable medium
        has_durable = any(
            str(step.get("channel", "")).lower() in durable_channels 
            for step in timeline
        )
        
        if not has_durable:
            # Insert the preferred durable medium
            timeline.insert(0, {
                "step": 1,
                "channel": preferred_durable,
                "when": "immediate",
                "purpose": f"✅ REGULATORY COMPLIANCE - Durable medium via {preferred_durable}",
                "why": f"Regulatory requirement met via {preferred_durable}",
                "compliance_note": f"FCA durable medium requirement satisfied via {preferred_durable}"
            })
            
            # Renumber other steps
            for i, step in enumerate(timeline[1:], start=2):
                step["step"] = i
        
        # Add regulatory compliance notice
        if "comms_plan" not in result:
            result["comms_plan"] = {}
        if "overrides_or_risks" not in result["comms_plan"]:
            result["comms_plan"]["overrides_or_risks"] = []
        
        # Update message to reflect new approach
        compliance_msg = f"✅ REGULATORY COMPLIANCE: Durable medium requirement met via {preferred_durable}"
        result["comms_plan"]["overrides_or_risks"].insert(0, compliance_msg)
        
        # Add cost savings note for digital customers
        if customer_category in ["Digital-first self-serve", "Assisted-digital"] and preferred_durable == "email":
            result["comms_plan"]["overrides_or_risks"].append(
                "💰 COST OPTIMIZATION: Using email as durable medium for digital-savvy customer (£1.46 saved per communication)")
        
        # Ensure formal tone in all communications
        self._ensure_formal_tone(result)
        
        # Add compliance tracking
        result["compliance_applied"] = True
        result["regulatory_channels"] = [preferred_durable]
        result["durable_medium_used"] = preferred_durable
        result["cost_optimized"] = preferred_durable != "letter"
        
        result["comms_plan"]["timeline"] = timeline
        return result
    
    def _apply_promotional_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for promotional communications."""
        self.logger.info("Applying promotional communication rules")
        
        # Check if customer is eligible for promotions
        customer_category = result.get("customer_category", {}).get("label", "")
        
        # BLOCK promotions for vulnerable customers
        if customer_category == "Vulnerable / extra-support":
            return self._block_promotional_content(result)
        
        # Enhance promotional content for eligible customers
        if result.get("upsell_included"):
            result = self._enhance_promotional_materials(result)
        
        # Add promotional compliance notes
        self._add_promotional_compliance(result)
        
        return result
    
    def _apply_information_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for informational communications."""
        self.logger.info("Applying informational communication rules")
        
        # Optimize for clarity and accessibility
        result = self._optimize_for_clarity(result)
        
        # Ensure multiple accessible formats for important info
        result = self._ensure_accessible_formats(result)
        
        return result
    
    def _ensure_formal_tone(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all regulatory communications use formal tone."""
        if "assets" in result:
            assets = result["assets"]
            
            # Update email subject to be formal
            if "email_html" in assets and isinstance(assets["email_html"], dict):
                subject = assets["email_html"].get("subject", "")
                if subject and not any(word in subject.lower() for word in ["important", "notice", "regulatory"]):
                    assets["email_html"]["subject"] = f"Important Regulatory Notice: {subject}"
            
            # Update SMS to be formal and include reference
            if "sms_text" in assets:
                sms = assets["sms_text"]
                if sms and not sms.startswith("IMPORTANT"):
                    assets["sms_text"] = f"IMPORTANT: {sms[:140]}"[:160]
        
        return result
    
    def _block_promotional_content(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Block all promotional content for vulnerable customers."""
        self.logger.warning("Blocking promotional content for vulnerable customer")
        
        # Force classification change
        result["classification"]["label"] = "INFORMATION"
        result["classification"]["reasoning"] = "Promotional content blocked for vulnerable customer protection"
        
        # Remove upsell
        result["upsell_included"] = False
        result["upsell_details"] = {
            "product": None,
            "reasoning": "Promotional content blocked for vulnerable customer",
            "message": None
        }
        
        # Add protection notice
        if "comms_plan" not in result:
            result["comms_plan"] = {}
        if "overrides_or_risks" not in result["comms_plan"]:
            result["comms_plan"]["overrides_or_risks"] = []
        
        result["comms_plan"]["overrides_or_risks"].insert(0,
            "🛡️ VULNERABLE CUSTOMER PROTECTION: Promotional content automatically blocked")
        
        return result
    
    def _enhance_promotional_materials(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance promotional materials for eligible customers."""
        if "assets" in result and result.get("upsell_details"):
            assets = result["assets"]
            upsell = result["upsell_details"]
            
            # Enhance email with better promotional content
            if "email_html" in assets and isinstance(assets["email_html"], dict):
                html = assets["email_html"].get("html", "")
                if html and upsell.get("message") and "💎" not in html:
                    promo_section = f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 20px; margin: 20px 0; border-radius: 8px;'>
                        <h3 style='color: white; margin: 0 0 10px 0;'>💎 Exclusive Offer</h3>
                        <p style='margin: 0 0 15px 0; font-size: 16px;'>{upsell['message']}</p>
                        <a href='#' style='background: white; color: #667eea; padding: 12px 24px; 
                           text-decoration: none; border-radius: 5px; font-weight: bold; 
                           display: inline-block;'>{upsell.get('cta', 'Learn More')}</a>
                    </div>
                    """
                    assets["email_html"]["html"] = html.replace("</body>", promo_section + "</body>")
            
            # Enhance in-app notification
            if "in_app_notification" in assets and upsell.get("message"):
                current = assets["in_app_notification"]
                if current and "💎" not in current:
                    assets["in_app_notification"] = current + f"\n\n💎 {upsell['message']}"
        
        return result
    
    def _add_promotional_compliance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add promotional compliance notices."""
        if "comms_plan" not in result:
            result["comms_plan"] = {}
        if "overrides_or_risks" not in result["comms_plan"]:
            result["comms_plan"]["overrides_or_risks"] = []
        
        # Add standard promotional disclaimers
        result["comms_plan"]["overrides_or_risks"].append(
            "📢 PROMOTIONAL: Standard terms and conditions apply to all offers")
        
        # Add to assets if needed
        if "assets" in result:
            for asset_key in ["email_html", "letter_docx_body"]:
                if asset_key in result["assets"]:
                    if asset_key == "email_html" and isinstance(result["assets"][asset_key], dict):
                        html = result["assets"][asset_key].get("html", "")
                        if html and "Terms and conditions apply" not in html:
                            disclaimer = "<p style='font-size: 12px; color: #666;'>Terms and conditions apply. See website for details.</p>"
                            result["assets"][asset_key]["html"] = html.replace("</body>", disclaimer + "</body>")
        
        return result
    
    def _optimize_for_clarity(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize informational content for clarity."""
        if "assets" in result:
            assets = result["assets"]
            
            # Make email subject clearer
            if "email_html" in assets and isinstance(assets["email_html"], dict):
                subject = assets["email_html"].get("subject", "")
                if subject and not any(word in subject.lower() for word in ["update", "information", "notice"]):
                    assets["email_html"]["subject"] = f"Account Information: {subject}"
            
            # Simplify SMS language
            if "sms_text" in assets:
                sms = assets["sms_text"]
                if sms and len(sms) > 140:
                    # Simplify if too long
                    assets["sms_text"] = "Account update available. Check app or call us for details."[:160]
        
        return result
    
    def _ensure_accessible_formats(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure accessible formats are available for informational content."""
        timeline = result.get("comms_plan", {}).get("timeline", [])
        
        # Check for accessibility needs
        customer_category = result.get("customer_category", {}).get("label", "")
        
        if customer_category == "Accessibility & alternate-format needs":
            # Ensure audio option exists
            has_audio = any(step.get("channel") == "audio" for step in timeline)
            if not has_audio:
                timeline.append({
                    "step": len(timeline) + 1,
                    "channel": "audio",
                    "when": "immediate",
                    "purpose": "Audio format for accessibility",
                    "why": "Ensuring information is accessible to all customers"
                })
        
        # For all customers, ensure clear communication
        has_in_app = any(step.get("channel") == "in_app" for step in timeline)
        if not has_in_app:
            timeline.append({
                "step": len(timeline) + 1,
                "channel": "in_app",
                "when": "immediate",
                "purpose": "Clear in-app notification",
                "why": "Convenient access to information"
            })
        
        # Renumber steps
        for i, step in enumerate(timeline):
            step["step"] = i + 1
        
        result.setdefault("comms_plan", {})["timeline"] = timeline
        return result