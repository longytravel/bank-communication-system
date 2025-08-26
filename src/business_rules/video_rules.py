"""
Video Communication Rules
Rules for determining video message eligibility and personalization.
WITH DEBUGGING FOR DATA ISSUES
"""

import logging
from typing import Dict, Any, List

class VideoEligibilityRules:
    """Rules for determining which customers qualify for personalized video messages."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration thresholds
        self.HIGH_VALUE_THRESHOLD = 10000  # £10,000 minimum balance
        self.MIN_DIGITAL_LOGINS = 10  # Minimum monthly digital logins
        self.MIN_AGE = 25  # Minimum age for video communications
        self.MAX_AGE = 65  # Maximum age for video communications
    
    def is_video_eligible(self, customer: Dict[str, Any], 
                         classification_type: str = None) -> Dict[str, Any]:
        """
        Determine if a customer qualifies for personalized video messages.
        
        Args:
            customer: Customer data dictionary
            classification_type: Type of communication (PROMOTIONAL, INFORMATION, etc.)
            
        Returns:
            Dictionary with eligibility status and reasoning
        """
        eligibility = {
            'eligible': False,
            'reasons': [],
            'score': 0,
            'tier': None
        }
        
        # Extract customer data with type conversion
        customer_name = customer.get('name', 'Unknown')
        category = customer.get('category', '')
        
        # CRITICAL: Convert account_balance to float if it's a string
        account_balance_raw = customer.get('account_balance', 0)
        try:
            # Handle string values like "15000" or "15,000"
            if isinstance(account_balance_raw, str):
                account_balance = float(account_balance_raw.replace(',', '').replace('£', ''))
            else:
                account_balance = float(account_balance_raw)
        except:
            account_balance = 0
            
        # Convert other numeric fields
        try:
            age = int(customer.get('age', 0)) if customer.get('age') else 0
            digital_logins = int(customer.get('digital_logins_per_month', 0)) if customer.get('digital_logins_per_month') else 0
        except:
            age = 0
            digital_logins = 0
            
        upsell_eligible = customer.get('upsell_eligible', False)
        financial_indicators = customer.get('financial_indicators', {})
        digital_maturity = financial_indicators.get('digital_maturity', 'none')
        account_health = financial_indicators.get('account_health', 'unknown')
        
        # DEBUG LOGGING
        if customer_name == "Digital Dave" or "Dave" in customer_name:
            self.logger.info(f"[DEBUG] DEBUGGING {customer_name}:")
            self.logger.info(f"  - Raw balance: {account_balance_raw} (type: {type(account_balance_raw)})")
            self.logger.info(f"  - Converted balance: £{account_balance:,.2f}")
            self.logger.info(f"  - Category: {category}")
            self.logger.info(f"  - Digital logins: {digital_logins}")
            self.logger.info(f"  - Age: {age}")
        
        # Score calculation (0-100)
        score = 0
        reasons = []
        
        # 1. Check customer category (40 points)
        if category == "Digital-first self-serve":
            score += 40
            reasons.append("Digital-first customer (+40)")
        elif category == "Assisted-digital":
            score += 20
            reasons.append("Assisted-digital customer (+20)")
        else:
            reasons.append(f"Not digitally active: '{category}' (0)")
            # Don't return early - let's see the full scoring
        
        # 2. Check account balance (30 points)
        if account_balance >= 50000:
            score += 30
            reasons.append(f"Ultra high-value customer (£{account_balance:,.0f}) (+30)")
            eligibility['tier'] = 'PLATINUM'
        elif account_balance >= 25000:
            score += 25
            reasons.append(f"Very high-value customer (£{account_balance:,.0f}) (+25)")
            eligibility['tier'] = 'GOLD'
        elif account_balance >= self.HIGH_VALUE_THRESHOLD:
            score += 20
            reasons.append(f"High-value customer (£{account_balance:,.0f}) (+20)")
            eligibility['tier'] = 'SILVER'
        else:
            reasons.append(f"Balance below threshold (£{account_balance:,.0f} < £{self.HIGH_VALUE_THRESHOLD}) (0)")
        
        # 3. Check digital engagement (15 points)
        if digital_logins >= 20:
            score += 15
            reasons.append(f"Highly engaged ({digital_logins} logins/month) (+15)")
        elif digital_logins >= self.MIN_DIGITAL_LOGINS:
            score += 10
            reasons.append(f"Good engagement ({digital_logins} logins/month) (+10)")
        elif digital_logins > 0:
            score += 5
            reasons.append(f"Some engagement ({digital_logins} logins/month) (+5)")
        else:
            reasons.append(f"No digital engagement (0)")
        
        # 4. Check age demographics (10 points)
        if self.MIN_AGE <= age <= self.MAX_AGE:
            score += 10
            reasons.append(f"Prime demographic (age {age}) (+10)")
        elif age < self.MIN_AGE and age > 0:
            score += 5
            reasons.append(f"Young demographic (age {age}) (+5)")
        else:
            reasons.append(f"Age outside target range ({age}) (0)")
        
        # 5. Check upsell eligibility (5 points)
        if upsell_eligible:
            score += 5
            reasons.append("Upsell eligible (+5)")
        
        # Determine final eligibility
        eligibility['score'] = score
        eligibility['reasons'] = reasons
        
        # DEBUG: Log scoring for Digital Dave
        if "Dave" in customer_name:
            self.logger.info(f"  - Final score: {score}/100")
            self.logger.info(f"  - Reasons: {reasons}")
        
        # Threshold for video eligibility (minimum 70 points)
        # TEMPORARY: Lower threshold for testing
        TESTING_THRESHOLD = 50  # Lowered from 70 for testing
        
        if score >= TESTING_THRESHOLD:
            eligibility['eligible'] = True
            self.logger.info(f"[OK] Customer {customer.get('customer_id')} eligible for video (score: {score})")
        else:
            self.logger.info(f"[X] Customer {customer.get('customer_id')} not eligible for video (score: {score} < {TESTING_THRESHOLD})")
        
        return eligibility
    
    def get_video_personalization_params(self, customer: Dict[str, Any], 
                                        eligibility: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalization parameters for video generation.
        
        Args:
            customer: Customer data
            eligibility: Eligibility assessment from is_video_eligible()
            
        Returns:
            Dictionary with video personalization parameters
        """
        params = {
            'avatar_type': 'professional_banker',
            'voice_tone': 'warm_professional',
            'background': 'modern_office',
            'duration_seconds': 15,
            'personalization_level': 'standard'
        }
        
        # Customize based on tier
        tier = eligibility.get('tier', 'SILVER')
        
        if tier == 'PLATINUM':
            params.update({
                'avatar_type': 'senior_banker',
                'background': 'executive_office',
                'duration_seconds': 20,
                'personalization_level': 'premium',
                'include_graphics': True,
                'custom_branding': True
            })
        elif tier == 'GOLD':
            params.update({
                'avatar_type': 'senior_banker',
                'background': 'premium_office',
                'duration_seconds': 18,
                'personalization_level': 'enhanced',
                'include_graphics': True
            })
        
        # Adjust for customer preferences
        age = customer.get('age', 40)
        try:
            age = int(age) if age else 40
        except:
            age = 40
            
        if age < 35:
            params['voice_tone'] = 'energetic_friendly'
            params['background'] = 'modern_tech'
        elif age > 55:
            params['voice_tone'] = 'calm_professional'
            params['background'] = 'traditional_office'
        
        return params
    
    def generate_video_script(self, customer: Dict[str, Any], 
                            communication_type: str,
                            products: List[str] = None) -> str:
        """
        Generate personalized video script based on customer profile.
        
        Args:
            customer: Customer data
            communication_type: Type of communication
            products: List of products to mention
            
        Returns:
            Personalized video script
        """
        name = customer.get('name', 'Valued Customer')
        first_name = name.split()[0] if name else 'Valued Customer'
        
        # Safe balance conversion
        account_balance_raw = customer.get('account_balance', 0)
        try:
            if isinstance(account_balance_raw, str):
                account_balance = float(account_balance_raw.replace(',', '').replace('£', ''))
            else:
                account_balance = float(account_balance_raw)
        except:
            account_balance = 0
            
        tier = 'premium' if account_balance >= 25000 else 'valued'
        
        # Base greeting
        greeting = f"Hello {first_name},"
        
        # Build script based on communication type
        if communication_type == "PROMOTIONAL" and products:
            script = f"""
            {greeting}
            
            As one of our {tier} customers, you've been specially selected for an exclusive opportunity.
            
            Based on your excellent account management and financial profile, you're pre-approved for our 
            {', '.join(products[:2]) if len(products) > 1 else products[0] if products else 'premium services'}.
            
            This comes with benefits tailored specifically for customers like you, including preferential rates 
            and premium features.
            
            Simply tap below to learn more, or speak with your personal banking advisor.
            
            Thank you for being a valued member of Resonance Bank.
            """
        
        elif communication_type == "INFORMATION":
            script = f"""
            {greeting}
            
            We have an important update about your account that deserves your attention.
            
            As a {tier} digital banking customer, you can review and action this directly through our app 
            in less than two minutes.
            
            Your financial security and convenience are our top priorities.
            
            Thank you for choosing Resonance Bank.
            """
        
        else:  # REGULATORY or other
            script = f"""
            {greeting}
            
            We're reaching out with important information about your account that requires your attention.
            
            As always, we're here to support you every step of the way.
            
            You can find full details in your secure message center, or contact us directly if you have 
            any questions.
            
            Thank you for your continued trust in Resonance Bank.
            """
        
        # Clean up script formatting
        script = ' '.join(script.split())  # Remove extra whitespace
        
        # Ensure script length is appropriate (150-200 words ideal for 15-20 seconds)
        word_count = len(script.split())
        if word_count > 200:
            # Truncate if too long
            words = script.split()[:200]
            script = ' '.join(words) + '...'
        
        return script
    
    def apply_video_rules(self, result: Dict[str, Any], 
                         customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply video eligibility rules to a communication strategy.
        
        Args:
            result: Communication strategy result
            customer: Customer data
            
        Returns:
            Modified result with video channel added if eligible
        """
        classification = result.get('classification', {}).get('label', 'INFORMATION')
        
        # Check eligibility
        eligibility = self.is_video_eligible(customer, classification)
        
        if eligibility['eligible']:
            self.logger.info(f"Adding video channel for customer {customer.get('customer_id')}")
            
            # Add video to channels
            timeline = result.get('comms_plan', {}).get('timeline', [])
            
            # Check if video already exists
            has_video = any(step.get('channel') == 'video_message' for step in timeline)
            
            if not has_video:
                # Add video as primary channel for high-value customers
                video_step = {
                    "step": 1,  # Make it first
                    "channel": "video_message",
                    "when": "immediate",
                    "purpose": f"Personalized video message for {eligibility.get('tier', 'valued')} customer",
                    "why": f"High-value digital customer (score: {eligibility['score']}/100)",
                    "tier": eligibility.get('tier', 'SILVER'),
                    "personalization": "Premium video experience"
                }
                
                # Insert at beginning and renumber other steps
                timeline.insert(0, video_step)
                for i, step in enumerate(timeline[1:], start=2):
                    step["step"] = i
                
                result.setdefault('comms_plan', {})['timeline'] = timeline
            
            # Add video script to assets
            if 'assets' not in result:
                result['assets'] = {}
            
            # Generate personalized script
            products = customer.get('upsell_products', [])
            script = self.generate_video_script(customer, classification, products)
            
            # Get personalization parameters
            video_params = self.get_video_personalization_params(customer, eligibility)
            
            result['assets']['video_message'] = {
                'script': script,
                'duration_seconds': video_params['duration_seconds'],
                'avatar_type': video_params['avatar_type'],
                'background': video_params['background'],
                'personalization_level': video_params['personalization_level'],
                'tier': eligibility.get('tier', 'SILVER'),
                'eligibility_score': eligibility['score'],
                'eligibility_reasons': eligibility['reasons']
            }
            
            # Add to personalization notes
            if 'personalization_notes' not in result:
                result['personalization_notes'] = []
            
            result['personalization_notes'].append(
                f"🎬 Premium video message added for {eligibility.get('tier', 'valued')} tier customer"
            )
            
            # Track video eligibility
            result['video_eligible'] = True
            result['video_tier'] = eligibility.get('tier', 'SILVER')
            result['video_score'] = eligibility['score']
        
        else:
            # Document why video wasn't added
            self.logger.info(
                f"Customer {customer.get('customer_id')} not eligible for video. "
                f"Score: {eligibility['score']}/100. Reasons: {eligibility['reasons']}"
            )
            
            result['video_eligible'] = False
            result['video_score'] = eligibility['score']
            result['video_ineligible_reasons'] = eligibility['reasons']
        
        return result
    
    def get_video_statistics(self, customers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about video eligibility across customer base.
        
        Args:
            customers: List of customer dictionaries
            
        Returns:
            Statistics about video eligibility
        """
        stats = {
            'total_customers': len(customers),
            'video_eligible': 0,
            'platinum_tier': 0,
            'gold_tier': 0,
            'silver_tier': 0,
            'average_score': 0,
            'eligibility_rate': 0
        }
        
        total_score = 0
        
        for customer in customers:
            eligibility = self.is_video_eligible(customer)
            
            if eligibility['eligible']:
                stats['video_eligible'] += 1
                
                tier = eligibility.get('tier', '')
                if tier == 'PLATINUM':
                    stats['platinum_tier'] += 1
                elif tier == 'GOLD':
                    stats['gold_tier'] += 1
                elif tier == 'SILVER':
                    stats['silver_tier'] += 1
            
            total_score += eligibility['score']
        
        if stats['total_customers'] > 0:
            stats['average_score'] = total_score / stats['total_customers']
            stats['eligibility_rate'] = (stats['video_eligible'] / stats['total_customers']) * 100
        
        return stats