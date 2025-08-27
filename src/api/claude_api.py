"""
Claude API Integration - Enhanced Multilingual Support
Handles all Claude API interactions with Polish, Urdu and other language support.
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
    Claude API wrapper with intelligent rate limiting, error handling, and multilingual support.
    """
    
    def __init__(self):
        """Initialize Claude API client with language configurations."""
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
        self.model = "claude-3-5-sonnet-20241022"  # Latest model
        self.default_max_tokens = 3500
        self.default_temperature = 0.2
        
        # Language mappings
        self.language_names = {
            'en': 'English', 'english': 'English',
            'es': 'Spanish', 'spanish': 'Spanish', 'español': 'Spanish',
            'fr': 'French', 'french': 'French', 'français': 'French',
            'de': 'German', 'german': 'German', 'deutsch': 'German',
            'it': 'Italian', 'italian': 'Italian', 'italiano': 'Italian',
            'pt': 'Portuguese', 'portuguese': 'Portuguese', 'português': 'Portuguese',
            'pl': 'Polish', 'polish': 'Polish', 'polski': 'Polish',  # NEW
            'ur': 'Urdu', 'urdu': 'Urdu', 'اردو': 'Urdu',  # NEW
            'zh': 'Mandarin Chinese', 'chinese': 'Mandarin Chinese', 'mandarin': 'Mandarin Chinese', '中文': 'Mandarin Chinese',
            'ar': 'Arabic', 'arabic': 'Arabic', 'عربي': 'Arabic',
            'hi': 'Hindi', 'hindi': 'Hindi', 'हिंदी': 'Hindi',
            'ja': 'Japanese', 'japanese': 'Japanese', '日本語': 'Japanese'
        }
        
        self.logger.info("Claude API initialized with multilingual support")
    
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
        Enhanced to preserve language preferences.
        """
        self.logger.info(f"Analyzing batch of {len(customers)} customers")
        
        # Sanitize customer data to prevent token overflow
        sanitized_customers = []
        for customer in customers:
            sanitized = self._sanitize_customer_data(customer)
            # Ensure language preference is preserved
            if 'preferred_language' in customer:
                sanitized['preferred_language'] = customer['preferred_language']
            sanitized_customers.append(sanitized)
        
        # Process in chunks to stay under rate limits
        all_results = []
        
        for i in range(0, len(sanitized_customers), batch_size):
            batch = sanitized_customers[i:i+batch_size]
            
            system_prompt = (
                "You are a precise multilingual customer analyst specializing in banking customer segmentation. "
                "Analyze customer data comprehensively, preserve language preferences, and provide JSON-only responses."
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
        Enhanced with multilingual support including Polish and Urdu.
        """
        self.logger.info(f"Processing letter for customer: {customer_profile.get('customer_id', 'unknown')}")
        
        # Detect customer's preferred language
        customer_language = customer_profile.get('preferred_language', 'English')
        self.logger.info(f"Customer language preference: {customer_language}")
        
        # Sanitize inputs
        safe_letter = self._truncate_text(letter_text, 6000)
        safe_profile = self._sanitize_customer_data(customer_profile, 600)
        
        # Get language-appropriate system prompt
        system_prompt = self._get_multilingual_system_prompt(customer_language)
        
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
            self.logger.info(f"Successfully processed letter in {customer_language}")
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
        
        system_prompt = "You are a multilingual letter classification expert. Provide precise JSON-only responses."
        
        user_prompt = f"""
        Classify this letter content (may be in any language):

        {safe_letter}

        Return JSON:
        {{
            "classification": "REGULATORY" | "PROMOTIONAL" | "INFORMATION",
            "confidence": 1-10,
            "reasoning": "detailed explanation",
            "key_indicators": ["phrases that led to classification"],
            "urgency": "low" | "medium" | "high",
            "detected_language": "language of the letter if identifiable"
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
    
    def _get_multilingual_system_prompt(self, language: str) -> str:
        """Get language-specific system prompt."""
        lang_lower = language.lower() if language else 'english'
        
        if lang_lower in ['polish', 'pl', 'polski']:
            return (
                "You are an expert banking communication strategist with fluency in Polish. "
                "Create highly personalized communication strategies using proper Polish grammar, "
                "including correct declension and conjugation. Understand Polish banking culture "
                "and formal communication standards. Always respond with valid JSON only."
            )
        elif lang_lower in ['urdu', 'ur', 'اردو']:
            return (
                "You are an expert banking communication strategist with fluency in Urdu. "
                "Create highly personalized communication strategies using proper Urdu script "
                "and respectful language. Understand Islamic banking principles and South Asian "
                "banking culture. Always respond with valid JSON only."
            )
        else:
            return (
                "You are an expert multilingual banking communication strategist. Create highly "
                "personalized communication strategies based on comprehensive customer analysis. "
                "Always respond with valid JSON only."
            )
    
    def _sanitize_customer_data(self, customer: Dict[str, Any], max_field_length: int = 400) -> Dict[str, Any]:
        """Sanitize customer data to prevent token overflow while preserving language info."""
        sanitized = {}
        
        # Important fields to preserve in full
        preserve_fields = ['preferred_language', 'customer_id', 'name', 'category']
        
        for key, value in customer.items():
            if key in preserve_fields:
                sanitized[key] = value
            elif isinstance(value, str):
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
        """Build prompt for customer analysis with language preservation."""
        return f"""
        Analyze each customer comprehensively. Consider ALL data fields including:
        - Transaction history, frequency, amounts
        - Account age, types, balances
        - Digital engagement patterns
        - Demographics and preferences INCLUDING preferred_language (MUST be preserved)
        - Financial stress indicators
        - Cultural and linguistic background

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
            "risk_factors": ["any concerns"],
            "preferred_language": "MUST preserve the original preferred_language from input data",
            "cultural_considerations": ["any cultural factors to consider for communication"]
        }}

        Return: {{"customer_categories": [array of customer objects]}}

        Customers to analyze:
        {json.dumps(customers, indent=2)}
        """
    
    def _build_letter_processing_prompt(self, letter: str, profile: Dict[str, Any], channels: List[str]) -> str:
        """Build prompt for letter processing with enhanced multilingual support."""
        # Get customer's language preference
        customer_language = profile.get('preferred_language', 'English')
        
        # Get the full language name
        lang_lower = customer_language.lower()
        lang_name = self.language_names.get(lang_lower, customer_language)
        
        # Build language-specific instructions
        language_instruction = self._get_language_instruction(lang_lower, lang_name)
        
        # Build cultural considerations
        cultural_notes = self._get_cultural_considerations(lang_lower)
        
        return f"""
        Create a HIGHLY PERSONALIZED communication strategy for this customer.
        
        {language_instruction}
        
        {cultural_notes}

        LETTER CONTENT:
        {letter}

        CUSTOMER PROFILE (analyze every field):
        {json.dumps(profile, indent=2)}

        AVAILABLE CHANNELS: {', '.join(channels)}

        Return comprehensive JSON with:
        {{
            "customer_categorization": {{
                "category": "string",
                "reasoning": ["detailed reasons"],
                "confidence": 1-10
            }},
            "communication_plan": {{
                "timeline": ["step by step plan"],
                "priority": "low|medium|high|urgent",
                "follow_up_schedule": ["dates/intervals"]
            }},
            "personalized_content": {{
                "email": {{
                    "subject": "in {lang_name}",
                    "body": "complete email in {lang_name}"
                }},
                "sms": {{
                    "message": "SMS text in {lang_name}"
                }},
                "letter": {{
                    "content": "formal letter in {lang_name}"
                }},
                "push_notification": {{
                    "title": "in {lang_name}",
                    "message": "in {lang_name}"
                }},
                "voice_note": {{
                    "script": "voice message script in {lang_name}"
                }}
            }},
            "upsell_analysis": {{
                "eligible": true|false,
                "reasoning": "detailed explanation",
                "recommended_products": ["list of products"] or [],
                "approach": "how to present offers"
            }},
            "personalization_elements": {{
                "tone": "formal|friendly|professional",
                "cultural_adaptations": ["specific cultural considerations applied"],
                "language_register": "formal|informal|business",
                "key_talking_points": ["personalized points based on customer data"]
            }}
        }}

        All customer-facing content MUST be in {lang_name}.
        Consider transaction patterns, account history, demographics, engagement, and cultural background.
        If vulnerable or high-risk, explain why no upsell is appropriate.
        """
    
    def _get_language_instruction(self, lang_lower: str, lang_name: str) -> str:
        """Get language-specific instructions for content generation."""
        
        if lang_lower in ['pl', 'polish', 'polski']:
            return f"""
            CRITICAL LANGUAGE REQUIREMENTS FOR POLISH:
            - Generate ALL customer-facing content in Polish
            - Use proper Polish grammar with correct declension and conjugation
            - Use Polish currency format: amounts in złoty (zł)
            - Use Polish date format: DD.MM.YYYY
            - Formal greetings: "Szanowny Panie" (Dear Sir) / "Szanowna Pani" (Dear Madam)
            - Use "Pan/Pani" + surname for formal address
            - Banking terms: konto (account), przelew (transfer), kredyt (credit), oszczędności (savings)
            - Keep JSON field names in English, but all values in Polish
            """
        
        elif lang_lower in ['ur', 'urdu', 'اردو']:
            return f"""
            CRITICAL LANGUAGE REQUIREMENTS FOR URDU:
            - Generate ALL customer-facing content in Urdu script
            - Use proper Urdu script (right-to-left writing)
            - Use respectful honorifics: "محترم" (Mohtaram) for respected
            - Address customers as: "جناب" (Janab) for Mr. / "محترمہ" (Mohtarma) for Ms.
            - Banking terms: کھاتہ (account), رقم (amount), قرض (loan), بچت (savings)
            - Currency: Pakistani Rupees (PKR) or as appropriate
            - Consider Islamic banking terminology if applicable
            - Keep JSON field names in English, but all values in Urdu
            - Use formal and highly respectful language throughout
            """
        
        elif lang_lower in ['es', 'spanish', 'español']:
            return f"""
            CRITICAL: Generate ALL content in Spanish!
            - All messages, emails, SMS, letters must be in Spanish
            - Use "Usted" for formal address
            - Formal greetings: "Estimado/a Sr./Sra."
            - Banking terms: cuenta, transferencia, crédito, ahorros
            - Keep field names in English, but all customer-facing text in Spanish
            """
        
        elif lang_lower in ['fr', 'french', 'français']:
            return f"""
            CRITICAL: Generate ALL content in French!
            - Use "Vous" for formal address
            - Formal greetings: "Monsieur/Madame"
            - Banking terms: compte, virement, crédit, épargne
            - Keep field names in English, but all customer-facing text in French
            """
        
        elif lang_lower in ['de', 'german', 'deutsch']:
            return f"""
            CRITICAL: Generate ALL content in German!
            - Use "Sie" for formal address
            - Formal greetings: "Sehr geehrter Herr/Sehr geehrte Frau"
            - Banking terms: Konto, Überweisung, Kredit, Ersparnisse
            - Keep field names in English, but all customer-facing text in German
            """
        
        else:
            return f"""
            CRITICAL: Generate ALL content in {lang_name}!
            - All messages, emails, SMS, letters must be in {lang_name}
            - Keep field names in English (like "email", "subject") 
            - But all customer-facing text in {lang_name}
            - Use culturally appropriate greetings and tone for {lang_name} speakers
            """
    
    def _get_cultural_considerations(self, lang_lower: str) -> str:
        """Get cultural considerations for communication."""
        
        if lang_lower in ['pl', 'polish', 'polski']:
            return """
            POLISH CULTURAL CONSIDERATIONS:
            - Poles value formality in banking communications
            - Use titles and surnames unless specifically invited to use first names
            - Be direct but polite - avoid excessive friendliness
            - Respect for hierarchy and authority is important
            - National holidays: Consider timing around Christmas, Easter, May holidays
            - Avoid communications on November 1st (All Saints' Day)
            """
        
        elif lang_lower in ['ur', 'urdu', 'اردو']:
            return """
            URDU/SOUTH ASIAN CULTURAL CONSIDERATIONS:
            - Maintain high formality and respect throughout
            - Consider Islamic banking principles (no interest/riba for Muslim customers)
            - Be aware of Islamic holidays: Ramadan, Eid ul-Fitr, Eid ul-Adha
            - Family financial decisions often involve multiple members
            - Prefer indirect communication style - be diplomatic
            - Morning communications are preferred
            - Avoid Friday afternoon communications (Jummah prayers)
            """
        
        elif lang_lower in ['ar', 'arabic', 'عربي']:
            return """
            ARABIC CULTURAL CONSIDERATIONS:
            - Consider Islamic banking principles
            - Respect religious holidays and prayer times
            - Use formal, respectful language
            - Family involvement in financial decisions is common
            """
        
        elif lang_lower in ['zh', 'chinese', 'mandarin', '中文']:
            return """
            CHINESE CULTURAL CONSIDERATIONS:
            - Numbers have cultural significance (8 is lucky, 4 is avoided)
            - Respect for hierarchy and saving face is important
            - Indirect communication style preferred
            - Consider timing around Chinese New Year and Golden Week
            """
        
        elif lang_lower in ['ja', 'japanese', '日本語']:
            return """
            JAPANESE CULTURAL CONSIDERATIONS:
            - Extreme politeness and formal language (keigo) required
            - Indirect communication style
            - Attention to detail is highly valued
            - Consider timing around Golden Week and Obon
            """
        
        else:
            return """
            GENERAL CULTURAL CONSIDERATIONS:
            - Use appropriate level of formality for the culture
            - Be aware of local holidays and customs
            - Respect cultural communication preferences
            """

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "model": self.model,
            "max_tokens": self.default_max_tokens,
            "temperature": self.default_temperature,
            "max_retries": self.max_retries,
            "status": "ready",
            "supported_languages": list(set(self.language_names.values())),
            "polish_support": "Full - Native content generation",
            "urdu_support": "Full - Native script and cultural awareness"
        }