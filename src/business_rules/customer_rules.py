"""
Customer Category Rules
Rules specific to different customer categories.
"""

import logging
from typing import Dict, Any

class CustomerCategoryRules:
    """Rules that apply based on customer category."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def apply_category_rules(self, result: Dict[str, Any], customer_category: str, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rules based on customer category."""
        
        if customer_category == "Digital-first self-serve":
            result = self._apply_digital_first_rules(result)
        
        elif customer_category == "Assisted-digital":
            result = self._apply_assisted_digital_rules(result)
        
        elif customer_category == "Low/no-digital (offline-preferred)":
            result = self._apply_low_digital_rules(result)
        
        elif customer_category == "Accessibility & alternate-format needs":
            result = self._apply_accessibility_rules(result)
        
        elif customer_category == "Vulnerable / extra-support":
            result = self._apply_vulnerable_rules(result)
        
        return result
    
    def _apply_digital_first_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for digital-first customers."""
        self.logger.info("Applying digital-first customer rules")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        
        # Remove phone channel - they prefer digital
        timeline = [step for step in timeline if step.get("channel") != "phone"]
        
        # Ensure in-app notification exists
        has_in_app = any(step.get("channel") == "in_app" for step in timeline)
        if not has_in_app:
            timeline.insert(0, {
                "step": 1,
                "channel": "in_app",
                "when": "immediate",
                "purpose": "Primary notification for digital-first customer",
                "why": "Digital-first customers prefer app notifications"
            })
        
        # Add voice note for convenience
        has_voice = any(step.get("channel") == "voice_note" for step in timeline)
        if not has_voice:
            timeline.append({
                "step": len(timeline) + 1,
                "channel": "voice_note", 
                "when": "immediate",
                "purpose": "Audio version for multitasking/convenience",
                "why": "Digital users often multitask and appreciate audio options"
            })
        
        # Renumber steps
        for i, step in enumerate(timeline):
            step["step"] = i + 1
        
        # Remove phone script from assets
        if "assets" in result and "phone_script" in result["assets"]:
            del result["assets"]["phone_script"]
        
        # Ensure we have a voice note text
        if "assets" in result and "voice_note_text" not in result["assets"]:
            in_app_text = result.get("assets", {}).get("in_app_notification", "")
            if in_app_text:
                result["assets"]["voice_note_text"] = in_app_text
        
        result.setdefault("comms_plan", {})["timeline"] = timeline
        return result
    
    def _apply_assisted_digital_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for assisted-digital customers."""
        self.logger.info("Applying assisted-digital customer rules")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        
        # Add coaching call option
        has_coaching = any("coaching" in str(step.get("purpose", "")).lower() for step in timeline)
        if not has_coaching:
            timeline.append({
                "step": len(timeline) + 1,
                "channel": "phone",
                "when": "+3 days",
                "purpose": "Optional coaching call for digital banking setup",
                "why": "Assisted-digital customers benefit from guided digital onboarding"
            })
        
        # Ensure helpful phone script
        if "assets" not in result:
            result["assets"] = {}
        
        if "phone_script" not in result["assets"]:
            result["assets"]["phone_script"] = (
                "Hi [Name], this is [Agent] from [Bank]. "
                "We noticed you received our recent communication. "
                "I'm calling to see if you'd like help setting up online banking or our mobile app. "
                "It can make managing your accounts much more convenient. "
                "Would you have 10 minutes for me to walk you through it?"
            )
        
        result.setdefault("comms_plan", {})["timeline"] = timeline
        return result
    
    def _apply_low_digital_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for low/no-digital customers."""
        self.logger.info("Applying low/no-digital customer rules")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        
        # Ensure letter delivery exists
        has_letter = any(step.get("channel") == "letter" for step in timeline)
        if not has_letter:
            timeline.insert(0, {
                "step": 1,
                "channel": "letter",
                "when": "immediate",
                "purpose": "Primary communication via preferred postal method",
                "why": "Low-digital customers prefer traditional postal communication"
            })
        
        # Add coaching call option
        has_coaching = any("coaching" in str(step.get("purpose", "")).lower() for step in timeline)
        if not has_coaching:
            timeline.append({
                "step": len(timeline) + 1,
                "channel": "phone",
                "when": "+5 days",
                "purpose": "Optional coaching call to introduce digital banking benefits",
                "why": "Gentle introduction to digital services for offline-preferred customers"
            })
        
        # Enhance letter with QR codes and simple digital onboarding
        if "assets" in result and "letter_docx_body" in result["assets"]:
            letter_body = result["assets"]["letter_docx_body"]
            if "QR" not in letter_body and "online" not in letter_body.lower():
                result["assets"]["letter_docx_body"] += (
                    "\n\nFor your convenience, you can also view this information online "
                    "or via our mobile app. Call us at [PHONE] if you'd like help getting started."
                )
        
        # Renumber steps
        for i, step in enumerate(timeline):
            step["step"] = i + 1
        
        result.setdefault("comms_plan", {})["timeline"] = timeline
        return result
    
    def _apply_accessibility_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for accessibility needs customers."""
        self.logger.info("Applying accessibility customer rules")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        
        # Ensure braille/audio options
        has_braille = any(step.get("channel") == "braille" for step in timeline)
        has_audio = any(step.get("channel") == "audio" for step in timeline)
        
        if not has_braille:
            timeline.append({
                "step": len(timeline) + 1,
                "channel": "braille",
                "when": "immediate",
                "purpose": "Accessible format for visually impaired customers",
                "why": "Ensuring equal access to information"
            })
        
        if not has_audio:
            timeline.append({
                "step": len(timeline) + 1,
                "channel": "audio",
                "when": "immediate", 
                "purpose": "Audio version for accessibility",
                "why": "Multiple accessible formats for different needs"
            })
        
        # Ensure braille text exists in assets
        if "assets" in result:
            if not result["assets"].get("braille_text_optional"):
                # Use simplified version of main message
                main_text = result.get("assets", {}).get("in_app_notification", "")
                if main_text:
                    result["assets"]["braille_text_optional"] = main_text
        
        # Renumber steps
        for i, step in enumerate(timeline):
            step["step"] = i + 1
        
        result.setdefault("comms_plan", {})["timeline"] = timeline
        return result
    
    def _apply_vulnerable_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Rules for vulnerable customers - handled in main engine for security."""
        self.logger.info("Applying vulnerable customer rules")
        
        timeline = result.get("comms_plan", {}).get("timeline", [])
        
        # Add proactive callback offer
        has_callback = any("callback" in str(step.get("purpose", "")).lower() for step in timeline)
        if not has_callback:
            timeline.insert(1, {
                "step": 2,
                "channel": "phone",
                "when": "+1 day",
                "purpose": "Proactive callback offer for vulnerable customer support",
                "why": "Vulnerable customers benefit from personal contact and reassurance"
            })
        
        # Ensure supportive phone script
        if "assets" not in result:
            result["assets"] = {}
        
        result["assets"]["phone_script"] = (
            "Hello [Name], this is [Agent] from [Bank]. "
            "We wanted to make sure you received and understood our recent communication. "
            "Is there anything we can help explain or any questions you might have? "
            "We're here to support you, and there's no rush. "
            "Would you prefer to discuss this now or schedule a callback at a more convenient time?"
        )
        
        # Renumber steps
        for i, step in enumerate(timeline):
            step["step"] = i + 1
        
        result.setdefault("comms_plan", {})["timeline"] = timeline
        return result