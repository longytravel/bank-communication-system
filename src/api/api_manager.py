"""
API Manager - FIXED VERSION
Coordinates all API interactions with proper language preservation.
No hardcoding - pure AI-driven multilingual support.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from .claude_api import ClaudeAPI
from .openai_api import OpenAIAPI
from .video_api import VideoAPI

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
        
        # After the OpenAI initialization, add Video API
        try:
            self.video = VideoAPI()
            self.logger.info("Video API initialized")
        except Exception as e:
            self.logger.warning(f"Video API not available: {e}")
            self.video = None
    
    def analyze_customer_base(self, customers: List[Dict[str, Any]], 
                            batch_size: int = 8) -> Optional[Dict[str, Any]]:
        """
        Analyze entire customer base for segmentation and insights.
        FIXED: Properly preserves all original customer data including language.
        """
        self.logger.info(f"Starting customer base analysis for {len(customers)} customers")
        
        # Log language preferences in original data
        language_summary = {}
        for customer in customers:
            lang = customer.get('preferred_language', 'Not Set')
            language_summary[lang] = language_summary.get(lang, 0) + 1
        self.logger.info(f"Customer languages in input: {language_summary}")
        
        # Get customer categories from Claude
        customer_categories = self.claude.analyze_customer_batch(customers, batch_size)
        
        if not customer_categories:
            self.logger.error("Failed to get customer categories from Claude")
            return None
        
        # CRITICAL FIX: Properly merge original data with Claude's analysis
        # This ensures ALL original fields are preserved, especially preferred_language
        for i, analyzed_customer in enumerate(customer_categories):
            if i < len(customers):
                original_customer = customers[i]
                
                # Log language preservation for key customers
                if 'Nowak' in original_customer.get('name', '') or 'Kowalski' in original_customer.get('name', ''):
                    self.logger.info(f"Polish customer {original_customer.get('name')}: "
                                   f"Original language = {original_customer.get('preferred_language')}")
                
                # COMPREHENSIVE MERGE: Original data takes precedence for factual fields
                # Claude's analysis adds categorization and insights
                
                # Fields where original data MUST take precedence (factual data)
                factual_fields = [
                    'customer_id', 'name', 'age', 'account_balance',
                    'preferred_language', 'email', 'phone',
                    'digital_logins_per_month', 'mobile_app_usage',
                    'email_opens_per_month', 'phone_calls_per_month',
                    'branch_visits_per_month', 'employment_status',
                    'income_level'
                ]
                
                # Preserve all factual fields from original
                for field in factual_fields:
                    if field in original_customer:
                        analyzed_customer[field] = original_customer[field]
                
                # Add any other original fields that Claude might have missed
                for key, value in original_customer.items():
                    if key not in analyzed_customer:
                        analyzed_customer[key] = value
                
                # Final verification log
                if 'Nowak' in analyzed_customer.get('name', '') or 'Kowalski' in analyzed_customer.get('name', ''):
                    self.logger.info(f"After merge: {analyzed_customer.get('name')} "
                                   f"has language = {analyzed_customer.get('preferred_language')}")
        
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
                "api_model": self.claude.model,
                "languages_present": language_summary
            }
        }
        
        self.logger.info(f"Customer base analysis completed. {len(customer_categories)} customers categorized.")
        return result
    
    def process_customer_communication(self, letter_text: str, customer_profile: Dict[str, Any],
                                     channels: List[str], generate_voice: bool = True) -> Optional[Dict[str, Any]]:
        """
        Process a complete customer communication strategy.
        FIXED: Ensures language preference is properly passed through.
        
        Args:
            letter_text: Original letter content
            customer_profile: Full customer profile INCLUDING preferred_language
            channels: Available communication channels
            generate_voice: Whether to generate voice notes
            
        Returns:
            Complete communication strategy with all assets
        """
        customer_id = customer_profile.get('customer_id', 'unknown')
        customer_language = customer_profile.get('preferred_language', 'English')
        
        self.logger.info(f"Processing communication for customer {customer_id} in {customer_language}")
        
        # CRITICAL: Ensure preferred_language is in the profile
        if 'preferred_language' not in customer_profile:
            self.logger.warning(f"No preferred_language for {customer_id}, defaulting to English")
            customer_profile['preferred_language'] = 'English'
        
        # Log the complete profile being sent to Claude
        if customer_language != 'English':
            self.logger.info(f"Sending to Claude: Customer {customer_profile.get('name')} "
                           f"with language={customer_language}")
        
        # Get communication strategy from Claude - it will use the language from profile
        strategy = self.claude.process_customer_letter(letter_text, customer_profile, channels)
        
        if not strategy:
            self.logger.error(f"Failed to get communication strategy for customer {customer_id}")
            return None
        
        # Ensure language is preserved in strategy
        strategy['customer_language'] = customer_language
        
        # Generate voice note if requested and customer is digital-first
        voice_note_path = None
        customer_category = strategy.get("customer_category", {}).get("label", "")
        
        if generate_voice and customer_category == "Digital-first self-serve":
            voice_note_path = self._generate_voice_note_for_customer(strategy, customer_id, customer_profile)
            
            if voice_note_path:
                # Add voice note to timeline if not already present
                timeline = strategy.get("comms_plan", {}).get("timeline", [])
                has_voice = any(step.get("channel") == "voice_note" for step in timeline)
                
                if not has_voice:
                    timeline.append({
                        "step": len(timeline) + 1,
                        "channel": "voice_note",
                        "when": "immediate",
                        "purpose": f"Audio version in {customer_language}",
                        "file_path": str(voice_note_path)
                    })
                    strategy.setdefault("comms_plan", {})["timeline"] = timeline
        
        # Generate video message if eligible
        if self.video and customer_profile.get('account_balance', 0) >= 10000:
            video_path = self._generate_video_for_customer(strategy, customer_id, customer_profile)
            if video_path:
                strategy['video_message_path'] = str(video_path)
        
        # Add API metadata
        strategy["processing_metadata"] = {
            "customer_id": customer_id,
            "customer_language": customer_language,
            "voice_note_generated": voice_note_path is not None,
            "voice_note_path": str(voice_note_path) if voice_note_path else None,
            "claude_model": self.claude.model,
            "channels_requested": channels
        }
        
        self.logger.info(f"Communication processing completed for customer {customer_id} in {customer_language}")
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
        results = {}
        
        for request in voice_requests:
            customer_id = request.get('customer_id')
            text = request.get('text', '')
            message_type = request.get('message_type', 'notification')
            customer_language = request.get('customer_language', request.get('preferred_language', None))
            
            file_path = self.openai.generate_voice_note(
                text, 
                customer_id, 
                message_type,
                customer_language=customer_language
            )
            results[customer_id] = file_path
        
        return results
    
    def generate_video_message(self, text: str, customer_id: str, 
                              message_type: str = "notification",
                              customer_data: Dict = None) -> Optional[Path]:
        """Generate video message with proper language support."""
        if not self.video:
            self.logger.warning("Video API not initialized")
            return None
        
        # Ensure language is passed to video generation
        if customer_data and 'preferred_language' not in customer_data:
            self.logger.warning(f"No language specified for video generation for {customer_id}")
        
        return self.video.generate_video_message(
            text, 
            customer_id, 
            message_type,
            customer_data=customer_data
        )
    
    def _generate_voice_note_for_customer(self, strategy: Dict[str, Any], customer_id: str, 
                                         customer_profile: Dict[str, Any] = None) -> Optional[Path]:
        """Generate voice note for a single customer's communication strategy."""
        
        # Get customer language - check multiple sources
        customer_language = (
            customer_profile.get('preferred_language') or
            strategy.get('customer_language') or
            strategy.get('preferred_language') or
            'English'
        )
        
        self.logger.info(f"Generating voice note for customer {customer_id} in {customer_language}")
        
        # Get text for voice note from strategy
        voice_text = None
        
        # Try different sources for voice text
        personalized_content = strategy.get("personalized_content", {})
        
        # Try voice_note first
        if "voice_note" in personalized_content:
            voice_text = personalized_content["voice_note"].get("script")
        
        # Try push notification
        if not voice_text and "push_notification" in personalized_content:
            push = personalized_content["push_notification"]
            voice_text = push.get("message", push.get("text"))
        
        # Try SMS
        if not voice_text and "sms" in personalized_content:
            voice_text = personalized_content["sms"].get("message")
        
        # Legacy support for old format
        if not voice_text:
            assets = strategy.get("assets", {})
            voice_text = (
                assets.get("voice_note_text") or
                assets.get("in_app_notification") or
                assets.get("sms_text")
            )
        
        if not voice_text:
            self.logger.warning(f"No suitable text found for voice note generation (customer {customer_id})")
            return None
        
        # Pass language to voice generation
        return self.openai.generate_voice_note(
            voice_text, 
            customer_id, 
            "notification",
            customer_language=customer_language
        )
    
    def _generate_video_for_customer(self, strategy: Dict[str, Any], customer_id: str,
                                    customer_profile: Dict[str, Any]) -> Optional[Path]:
        """Generate video message for eligible customers."""
        if not self.video:
            return None
        
        # Get video script from strategy
        personalized_content = strategy.get("personalized_content", {})
        video_text = None
        
        # Try to get video-specific content
        if "video_message" in personalized_content:
            video_text = personalized_content["video_message"].get("script")
        
        # Fallback to email content
        if not video_text and "email" in personalized_content:
            # Use email subject + first paragraph
            email = personalized_content["email"]
            subject = email.get("subject", "")
            body = email.get("body", "")
            first_para = body.split('\n')[0] if body else ""
            video_text = f"{subject}. {first_para}"[:500]  # Limit length
        
        if not video_text:
            return None
        
        # Generate video with full customer data (includes language)
        return self.video.generate_video_message(
            video_text,
            customer_id,
            "personalized",
            customer_data=customer_profile
        )
    
    def _build_aggregates(self, customer_categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build aggregate statistics from customer categories."""
        total = len(customer_categories)
        
        if total == 0:
            return {"total_customers": 0, "categories": {}, "insights": []}
        
        # Count categories and languages
        category_counts = {}
        language_counts = {}
        upsell_eligible = 0
        accessibility_count = 0
        vulnerable_count = 0
        
        for customer in customer_categories:
            # Category counts
            category = customer.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Language counts
            language = customer.get("preferred_language", "Unknown")
            language_counts[language] = language_counts.get(language, 0) + 1
            
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
        
        # Add language diversity insight
        if len(language_counts) > 1:
            non_english = sum(count for lang, count in language_counts.items() if lang != 'English')
            insights.append(f"{pct(non_english)} require non-English communication")
        
        if accessibility_count > 0:
            insights.append(f"{pct(accessibility_count)} need alternate formats — ensure braille/audio availability")
        
        if vulnerable_count > 0:
            insights.append(f"{pct(vulnerable_count)} require extra support — no promotional content for these customers")
        
        return {
            "total_customers": total,
            "categories": category_counts,
            "languages": language_counts,
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
                "opportunities": ["In-app nudges", "Voice notes", "Email/SMS reminders", "Video messages for high-value"]
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
            "openai": {"status": "unknown", "model": None, "error": None},
            "video": {"status": "unknown", "model": None, "error": None}
        }
        
        # Check Claude
        try:
            claude_info = self.claude.get_model_info()
            status["claude"] = {
                "status": "connected",
                "model": claude_info.get("model"),
                "max_tokens": claude_info.get("max_tokens"),
                "supported_languages": claude_info.get("supported_languages", []),
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
                "supported_languages": openai_info.get("supported_languages", []),
                "error": None
            }
        except Exception as e:
            status["openai"] = {
                "status": "error",
                "model": None,
                "error": str(e)
            }
        
        # Check Video (D-ID)
        if self.video:
            try:
                video_languages = self.video.get_supported_languages()
                status["video"] = {
                    "status": "connected",
                    "provider": "D-ID",
                    "supported_languages": [lang['name'] for lang in video_languages],
                    "error": None
                }
            except Exception as e:
                status["video"] = {
                    "status": "error",
                    "provider": "D-ID",
                    "error": str(e)
                }
        else:
            status["video"] = {
                "status": "not initialized",
                "provider": None,
                "error": "Video API not available"
            }
        
        return status
    
    def test_all_apis(self) -> Dict[str, Any]:
        """Test all API connections with simple requests."""
        results = {
            "claude": {"success": False, "error": None, "response_time": None},
            "openai": {"success": False, "error": None, "response_time": None},
            "video": {"success": False, "error": None, "response_time": None}
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
        
        # Test Video (D-ID)
        if self.video:
            try:
                start_time = time.time()
                test_path = self.video.test_video_generation()
                
                if test_path and test_path.exists():
                    results["video"]["success"] = True
                    results["video"]["response_time"] = round(time.time() - start_time, 2)
                else:
                    results["video"]["error"] = "Video generation failed"
            except Exception as e:
                results["video"]["error"] = str(e)
        else:
            results["video"]["error"] = "Video API not initialized"
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all APIs."""
        stats = {
            "voice_notes": self.openai.get_voice_note_stats() if hasattr(self.openai, 'get_voice_note_stats') else {},
            "claude_model": self.claude.model,
            "openai_model": self.openai.tts_model
        }
        
        # Add video stats if available
        if self.video and hasattr(self.video, 'get_video_stats'):
            stats["video_messages"] = self.video.get_video_stats()
        
        return stats
    
    def cleanup_resources(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old resources (voice notes, videos, etc.)."""
        cleanup_results = {}
        
        # Clean up voice notes
        if hasattr(self.openai, 'cleanup_old_voice_notes'):
            cleanup_results["voice_notes_deleted"] = self.openai.cleanup_old_voice_notes(days_old)
        
        # Clean up videos
        if self.video and hasattr(self.video, 'cleanup_old_videos'):
            cleanup_results["videos_deleted"] = self.video.cleanup_old_videos(days_old)
        
        self.logger.info(f"Resource cleanup completed: {cleanup_results}")
        return cleanup_results