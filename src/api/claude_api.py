"""
Claude API Integration
Handles all Claude API interactions with rate limiting and error handling.
"""

import logging
import time
import random
import json
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_key

class ClaudeAPI:
    """
    Claude API wrapper with intelligent rate limiting and error handling.
    """
    
    def __init__(self):
        """Initialize Claude API client."""
        self.logger = logging.getLogger(__name__)
        
        # Get API key from config
        api_key = get_api_key('claude')
        if not api_key:
            raise ValueError("Claude API key not found. Check your .env file.")
        
        self.client = Anthropic(api_key=api_key)
        
        # Rate limiting settings
        self.max_retries = 6
        self.base_delay = 2.0
        self.max_delay = 30.0
        
        # Model settings
        self.model = "claude-sonnet-4-20250514"  # Latest model
        self.default_max_tokens = 3500
        self.default_temperature = 0.2
        
        self.logger.info("Claude API initialized successfully")
    
    def _with_exponential_backoff(self, **kwargs):
        """
        Call Claude API with exponential backoff for rate limit handling.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.messages.create(**kwargs)
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                is_rate_limit = any(term in error_msg for term in [
                    "429", "rate_limit", "rate limit", "too many requests", 
                    "rps", "tokens per minute"
                ])
                
                if is_rate_limit and attempt < self.max_retries:
                    # Exponential backoff with jitter
                    sleep_time = min(
                        self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1),
                        self.max_delay
                    )
                    
                    self.logger.warning(f"Rate limit hit. Retrying in {sleep_time:.1f}s (attempt {attempt}/{self.max_retries})")
                    time.sleep(sleep_time)
                    continue
                
                # Re-raise if not rate limit or max retries reached
                self.logger.error(f"Claude API error: {e}")
                raise
        
        raise Exception(f"Failed after {self.max_retries} attempts")
    
    def analyze_customer_batch(self, customers: List[Dict[str, Any]], batch_size: int = 8) -> Optional[List[Dict[str, Any]]]:
        """
        Analyze a batch of customers for categorization and upsell opportunities.
        """
        self.logger.info(f"Analyzing batch of {len(customers)} customers")
        
        # Sanitize customer data to prevent token overflow
        sanitized_customers = []
        for customer in customers:
            sanitized = self._sanitize_customer_data(customer)
            sanitized_customers.append(sanitized)
        
        # Process in chunks to stay under rate limits
        all_results = []
        
        for i in range(0, len(sanitized_customers), batch_size):
            batch = sanitized_customers[i:i+batch_size]
            
            system_prompt = (
                "You are a precise customer analyst specializing in banking customer segmentation. "
                "Analyze customer data comprehensively and provide JSON-only responses."
            )
            
            user_prompt = self._build_customer_analysis_prompt(batch)
            
            try:
                response = self._with_exponential_backoff(
                    model=self.model,
                    max_tokens=self.default_max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=self.default_temperature
                )
                
                # Parse response
                result = self._safe_json_parse(response.content[0].text)
                batch_results = result.get("customer_categories", [])
                
                if isinstance(batch_results, list):
                    all_results.extend(batch_results)
                else:
                    self.logger.warning(f"Unexpected batch result format: {type(batch_results)}")
                
                # Small delay between batches
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing customer batch: {e}")
                return None
        
        self.logger.info(f"Successfully analyzed {len(all_results)} customers")
        return all_results
    
    def process_customer_letter(self, letter_text: str, customer_profile: Dict[str, Any], 
                              allowed_channels: List[str]) -> Optional[Dict[str, Any]]:
        """
        Process a letter for a specific customer to create personalized communication strategy.
        """
        self.logger.info(f"Processing letter for customer: {customer_profile.get('customer_id', 'unknown')}")
        
        # Sanitize inputs
        safe_letter = self._truncate_text(letter_text, 6000)
        safe_profile = self._sanitize_customer_data(customer_profile, 600)
        
        system_prompt = (
            "You are an expert banking communication strategist. Create highly personalized "
            "communication strategies based on comprehensive customer analysis. "
            "Always respond with valid JSON only."
        )
        
        user_prompt = self._build_letter_processing_prompt(safe_letter, safe_profile, allowed_channels)
        
        try:
            response = self._with_exponential_backoff(
                model=self.model,
                max_tokens=self.default_max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.3  # Slightly more creative for personalization
            )
            
            result = self._safe_json_parse(response.content[0].text)
            self.logger.info("Successfully processed customer letter")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing customer letter: {e}")
            return None
    
    def classify_letter(self, letter_text: str) -> Optional[Dict[str, Any]]:
        """
        Classify a letter as REGULATORY, PROMOTIONAL, or INFORMATION.
        """
        self.logger.info("Classifying letter content")
        
        safe_letter = self._truncate_text(letter_text, 3000)
        
        system_prompt = "You are a letter classification expert. Provide precise JSON-only responses."
        
        user_prompt = f"""
        Classify this letter content:

        {safe_letter}

        Return JSON:
        {{
            "classification": "REGULATORY" | "PROMOTIONAL" | "INFORMATION",
            "confidence": 1-10,
            "reasoning": "detailed explanation",
            "key_indicators": ["phrases that led to classification"],
            "urgency": "low" | "medium" | "high"
        }}
        """
        
        try:
            response = self._with_exponential_backoff(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.1  # Very consistent for classification
            )
            
            result = self._safe_json_parse(response.content[0].text)
            self.logger.info(f"Classified letter as: {result.get('classification', 'unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error classifying letter: {e}")
            return None
    
    def _sanitize_customer_data(self, customer: Dict[str, Any], max_field_length: int = 400) -> Dict[str, Any]:
        """Sanitize customer data to prevent token overflow."""
        sanitized = {}
        
        for key, value in customer.items():
            if isinstance(value, str):
                sanitized[key] = self._truncate_text(value, max_field_length)
            elif isinstance(value, (int, float, bool)) or value is None:
                sanitized[key] = value
            else:
                # Convert complex objects to strings safely
                try:
                    sanitized[key] = self._truncate_text(str(value), max_field_length)
                except Exception:
                    sanitized[key] = "complex_data"
        
        return sanitized
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to prevent token overflow."""
        if isinstance(text, str) and len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON from Claude's response."""
        # Clean up response
        cleaned = text.strip()
        
        # Remove code fences if present
        if cleaned.startswith("```"):
            lines = cleaned.split('\n')
            if lines[0].lower().startswith("```json"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = '\n'.join(lines).strip()
        
        # Try to find JSON object
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = cleaned[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON parse error: {e}")
                pass
        
        # Fallback: try parsing the whole thing
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON response from Claude: {text[:200]}...")
    
    def _build_customer_analysis_prompt(self, customers: List[Dict[str, Any]]) -> str:
        """Build prompt for customer analysis."""
        return f"""
        Analyze each customer comprehensively. Consider ALL data fields including:
        - Transaction history, frequency, amounts
        - Account age, types, balances
        - Digital engagement patterns
        - Demographics and preferences
        - Financial stress indicators

        For each customer, return:
        {{
            "customer_id": "string",
            "name": "string", 
            "category": "Digital-first self-serve"|"Assisted-digital"|"Low/no-digital (offline-preferred)"|"Accessibility & alternate-format needs"|"Vulnerable / extra-support",
            "category_reasoning": ["specific data points for this categorization"],
            "upsell_eligible": true|false,
            "upsell_eligibility_reasoning": "detailed explanation",
            "upsell_products": ["product names"] or [],
            "financial_indicators": {{
                "account_health": "healthy"|"stressed"|"vulnerable",
                "engagement_level": "high"|"medium"|"low",
                "digital_maturity": "advanced"|"moderate"|"basic"|"none"
            }},
            "support_needs": ["specific needs"],
            "preferred_channels": ["channel names"],
            "risk_factors": ["any concerns"]
        }}

        Return: {{"customer_categories": [array of customer objects]}}

        Customers to analyze:
        {json.dumps(customers, indent=2)}
        """
    
    def _build_letter_processing_prompt(self, letter: str, profile: Dict[str, Any], channels: List[str]) -> str:
        """Build prompt for letter processing."""
        return f"""
        Create a HIGHLY PERSONALIZED communication strategy for this customer.

        LETTER CONTENT:
        {letter}

        CUSTOMER PROFILE (analyze every field):
        {json.dumps(profile, indent=2)}

        AVAILABLE CHANNELS: {', '.join(channels)}

        Return comprehensive JSON with:
        - Detailed customer categorization with reasoning
        - Communication plan with timeline
        - All assets (email, SMS, letter, audio, etc.)
        - Upsell analysis (if NOT eligible, explain WHY in detail)
        - Personalization based on their specific data

        Consider their transaction patterns, account history, demographics, and engagement.
        If vulnerable or high-risk, explain why no upsell is appropriate.
        """

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "model": self.model,
            "max_tokens": self.default_max_tokens,
            "temperature": self.default_temperature,
            "max_retries": self.max_retries,
            "status": "ready"
        }