"""
API Manager
Coordinates all API interactions and provides a unified interface.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from .claude_api import ClaudeAPI
from .openai_api import OpenAIAPI

class APIManager:
    """
    Unified interface for all API interactions.
    Handles coordination between Claude and OpenAI APIs.
    """
    
    def __init__(self):
        """Initialize all API clients."""
        self.logger = logging.getLogger(__name__)
        
        try:
            self.claude = ClaudeAPI()
            self.openai = OpenAIAPI()
            self.logger.info("API Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize API Manager: {e}")
            raise
    
    def analyze_customer_base(self, customers: List[Dict[str, Any]], 
                            batch_size: int = 8) -> Optional[Dict[str, Any]]:
        """
        Analyze entire customer base for segmentation and insights.
        
        Args:
            customers: List of customer records
            batch_size: Number of customers per API batch
            
        Returns:
            Complete analysis with categories, aggregates, and summaries
        """
        self.logger.info(f"Starting customer base analysis for {len(customers)} customers")
        
        # Get customer categories from Claude
        customer_categories = self.claude.analyze_customer_batch(customers, batch_size)
        
        if not customer_categories:
            self.logger.error("Failed to get customer categories from Claude")
            return None
        
        # Build aggregated insights
        aggregates = self._build_aggregates(customer_categories)
        segment_summaries = self._build_segment_summaries(aggregates)
        
        result = {
            "customer_categories": customer_categories,
            "aggregates": aggregates,
            "segment_summaries": segment_summaries,
            "analysis_metadata": {
                "total_analyzed": len(customer_categories),
                "batch_size_used": batch_size,
                "api_model": self.claude.model
            }
        }
        
        self.logger.info(f"Customer base analysis completed. {len(customer_categories)} customers categorized.")
        return result
    
    def process_customer_communication(self, letter_text: str, customer_profile: Dict[str, Any],
                                     channels: List[str], generate_voice: bool = True) -> Optional[Dict[str, Any]]:
        """
        Process a complete customer communication strategy.
        
        Args:
            letter_text: Original letter content
            customer_profile: Full customer profile
            channels: Available communication channels
            generate_voice: Whether to generate voice notes
            
        Returns:
            Complete communication strategy with all assets
        """
        customer_id = customer_profile.get('customer_id', 'unknown')
        self.logger.info(f"Processing communication for customer {customer_id}")
        
        # Get communication strategy from Claude
        strategy = self.claude.process_customer_letter(letter_text, customer_profile, channels)
        
        if not strategy:
            self.logger.error(f"Failed to get communication strategy for customer {customer_id}")
            return None
        
        # Generate voice note if requested and customer is digital-first
        voice_note_path = None
        customer_category = strategy.get("customer_category", {}).get("label", "")
        
        if generate_voice and customer_category == "Digital-first self-serve":
            voice_note_path = self._generate_voice_note_for_customer(strategy, customer_id)
            
            if voice_note_path:
                # Add voice note to timeline if not already present
                timeline = strategy.get("comms_plan", {}).get("timeline", [])
                has_voice = any(step.get("channel") == "voice_note" for step in timeline)
                
                if not has_voice:
                    timeline.append({
                        "step": len(timeline) + 1,
                        "channel": "voice_note",
                        "when": "immediate",
                        "purpose": "Audio version for convenient listening",
                        "file_path": str(voice_note_path)
                    })
                    strategy.setdefault("comms_plan", {})["timeline"] = timeline
        
        # Add API metadata
        strategy["processing_metadata"] = {
            "customer_id": customer_id,
            "voice_note_generated": voice_note_path is not None,
            "voice_note_path": str(voice_note_path) if voice_note_path else None,
            "claude_model": self.claude.model,
            "channels_requested": channels
        }
        
        self.logger.info(f"Communication processing completed for customer {customer_id}")
        return strategy
    
    def classify_letter(self, letter_text: str) -> Optional[Dict[str, Any]]:
        """
        Classify letter content using Claude.
        
        Args:
            letter_text: Letter content to classify
            
        Returns:
            Classification result with confidence and reasoning
        """
        return self.claude.classify_letter(letter_text)
    
    def generate_voice_notes_batch(self, voice_requests: List[Dict[str, Any]]) -> Dict[str, Optional[Path]]:
        """
        Generate voice notes for multiple customers.
        
        Args:
            voice_requests: List of voice generation requests
            
        Returns:
            Dict mapping customer_id to generated file path
        """
        return self.openai.generate_voice_notes_batch(voice_requests)
    
    def _generate_voice_note_for_customer(self, strategy: Dict[str, Any], customer_id: str) -> Optional[Path]:
        """Generate voice note for a single customer's communication strategy."""
        
        # Get text for voice note from strategy
        voice_text = None
        
        # Try voice_note_text from assets first
        assets = strategy.get("assets", {})
        voice_text = assets.get("voice_note_text")
        
        # Fallback to in-app notification
        if not voice_text:
            voice_text = assets.get("in_app_notification")
        
        # Fallback to SMS text
        if not voice_text:
            voice_text = assets.get("sms_text")
        
        if not voice_text:
            self.logger.warning(f"No suitable text found for voice note generation (customer {customer_id})")
            return None
        
        return self.openai.generate_voice_note(voice_text, customer_id, "notification")
    
    def _build_aggregates(self, customer_categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build aggregate statistics from customer categories."""
        total = len(customer_categories)
        
        if total == 0:
            return {"total_customers": 0, "categories": {}, "insights": []}
        
        # Count categories
        category_counts = {}
        upsell_eligible = 0
        accessibility_count = 0
        vulnerable_count = 0
        
        for customer in customer_categories:
            category = customer.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
            
            if customer.get("upsell_eligible"):
                upsell_eligible += 1
            
            if category == "Accessibility & alternate-format needs":
                accessibility_count += 1
            
            if category == "Vulnerable / extra-support":
                vulnerable_count += 1
        
        # Generate insights
        def pct(count):
            return f"{(count/total*100):.0f}%" if total > 0 else "0%"
        
        top_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "None"
        
        insights = [
            f"{pct(category_counts.get(top_category, 0))} of customers are {top_category} — prioritize their preferred channels",
            f"Upsell eligibility at {pct(upsell_eligible)} suggests targeted but respectful approach",
        ]
        
        if accessibility_count > 0:
            insights.append(f"{pct(accessibility_count)} need alternate formats — ensure braille/audio availability")
        
        if vulnerable_count > 0:
            insights.append(f"{pct(vulnerable_count)} require extra support — no promotional content for these customers")
        
        return {
            "total_customers": total,
            "categories": category_counts,
            "upsell_eligible_count": upsell_eligible,
            "accessibility_needs_count": accessibility_count,
            "vulnerable_count": vulnerable_count,
            "insights": insights[:4]  # Keep top 4 insights
        }
    
    def _build_segment_summaries(self, aggregates: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build segment summaries for strategic planning."""
        categories = aggregates.get("categories", {})
        segments = []
        
        # Define segment characteristics
        segment_info = {
            "Digital-first self-serve": {
                "description": "Comfortable with apps and email; quick to act on concise messages",
                "opportunities": ["In-app nudges", "Voice notes", "Email/SMS reminders"]
            },
            "Assisted-digital": {
                "description": "Uses digital but benefits from guidance; appreciates blended support",
                "opportunities": ["Guided email with help links", "Follow-up coaching calls"]
            },
            "Low/no-digital (offline-preferred)": {
                "description": "Prefers paper/phone; opportunity for digital coaching",
                "opportunities": ["Clear letters with QR codes", "Digital coaching calls"]
            },
            "Accessibility & alternate-format needs": {
                "description": "Requires alternate formats or accommodations",
                "opportunities": ["Braille/audio packs", "High-contrast templates"]
            },
            "Vulnerable / extra-support": {
                "description": "Needs softer tone and extra care; callback offers essential",
                "opportunities": ["Proactive callbacks", "Extended response windows", "No sales pressure"]
            }
        }
        
        for category, count in categories.items():
            if count > 0 and category in segment_info:
                info = segment_info[category]
                segments.append({
                    "segment": category,
                    "size": count,
                    "description": info["description"],
                    "opportunities": info["opportunities"]
                })
        
        # Sort by size (largest first)
        segments.sort(key=lambda x: x["size"], reverse=True)
        return segments
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get status of all API connections."""
        status = {
            "claude": {"status": "unknown", "model": None, "error": None},
            "openai": {"status": "unknown", "model": None, "error": None}
        }
        
        # Check Claude
        try:
            claude_info = self.claude.get_model_info()
            status["claude"] = {
                "status": "connected",
                "model": claude_info.get("model"),
                "max_tokens": claude_info.get("max_tokens"),
                "error": None
            }
        except Exception as e:
            status["claude"] = {
                "status": "error",
                "model": None,
                "error": str(e)
            }
        
        # Check OpenAI
        try:
            openai_info = self.openai.get_model_info()
            status["openai"] = {
                "status": "connected",
                "tts_model": openai_info.get("tts_model"),
                "default_voice": openai_info.get("default_voice"),
                "error": None
            }
        except Exception as e:
            status["openai"] = {
                "status": "error",
                "model": None,
                "error": str(e)
            }
        
        return status
    
    def test_all_apis(self) -> Dict[str, Any]:
        """Test all API connections with simple requests."""
        results = {
            "claude": {"success": False, "error": None, "response_time": None},
            "openai": {"success": False, "error": None, "response_time": None}
        }
        
        # Test Claude with simple classification
        try:
            import time
            start_time = time.time()
            
            test_result = self.claude.classify_letter("This is a test message about account information.")
            
            if test_result and "classification" in test_result:
                results["claude"]["success"] = True
                results["claude"]["response_time"] = round(time.time() - start_time, 2)
            else:
                results["claude"]["error"] = "Invalid response format"
                
        except Exception as e:
            results["claude"]["error"] = str(e)
        
        # Test OpenAI with voice generation
        try:
            start_time = time.time()
            
            test_path = self.openai.test_voice_generation("This is a test.")
            
            if test_path and test_path.exists():
                results["openai"]["success"] = True
                results["openai"]["response_time"] = round(time.time() - start_time, 2)
                # Clean up test file
                test_path.unlink()
            else:
                results["openai"]["error"] = "Voice generation failed"
                
        except Exception as e:
            results["openai"]["error"] = str(e)
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all APIs."""
        stats = {
            "voice_notes": self.openai.get_voice_note_stats(),
            "claude_model": self.claude.model,
            "openai_model": self.openai.tts_model
        }
        
        return stats
    
    def cleanup_resources(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old resources (voice notes, etc.)."""
        cleanup_results = {
            "voice_notes_deleted": self.openai.cleanup_old_voice_notes(days_old)
        }
        
        self.logger.info(f"Resource cleanup completed: {cleanup_results}")
        return cleanup_results