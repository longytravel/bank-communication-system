"""
Create a reusable test dataset for quick testing
This creates pre-analyzed customer data so we don't have to run analysis every time!
"""

import json
from pathlib import Path
from datetime import datetime

# Create test customers with FULL analysis already done
TEST_CUSTOMERS = {
    "customer_categories": [
        {
            # MARIA - Spanish speaker, middle value
            "customer_id": "CUST011",
            "name": "Maria Garcia",
            "age": 35,
            "account_balance": 25000,
            "digital_logins_per_month": 18,
            "email": "maria.garcia@email.com",
            "phone": "+44 7700 900123",
            "preferred_language": "Spanish",  # CRITICAL for testing
            "category": "Digital-first self-serve",
            "category_reasoning": [
                "18 digital logins per month shows high engagement",
                "Age 35 in prime digital demographic",
                "£25,000 balance indicates established customer"
            ],
            "upsell_eligible": True,
            "upsell_eligibility_reasoning": "Strong balance and engagement",
            "upsell_products": ["Premium Account", "Travel Insurance"],
            "financial_indicators": {
                "account_health": "healthy",
                "engagement_level": "high", 
                "digital_maturity": "advanced"
            },
            "support_needs": [],
            "preferred_channels": ["in_app", "email", "voice_note"],
            "risk_factors": []
        },
        {
            # VERA - Vulnerable customer needing protection
            "customer_id": "CUST002",
            "name": "Vulnerable Vera",
            "age": 78,
            "account_balance": 3500,
            "digital_logins_per_month": 0,
            "email": "vera.jones@email.com",
            "phone": "+44 7700 900456",
            "preferred_language": "English",
            "category": "Vulnerable / extra-support",
            "category_reasoning": [
                "Age 78 requires extra care",
                "No digital engagement",
                "May need support with communications"
            ],
            "upsell_eligible": False,  # MUST BE FALSE for vulnerable
            "upsell_eligibility_reasoning": "Vulnerable customer - no sales",
            "upsell_products": [],
            "financial_indicators": {
                "account_health": "vulnerable",
                "engagement_level": "low",
                "digital_maturity": "none"
            },
            "support_needs": ["Large print", "Phone support", "Extra time"],
            "preferred_channels": ["letter", "phone"],
            "risk_factors": ["Age", "No digital access", "Potential scam target"]
        },
        {
            # DAVE - Digital native, high value
            "customer_id": "CUST001", 
            "name": "Digital Dave",
            "age": 32,
            "account_balance": 50000,  # High value for video eligibility
            "digital_logins_per_month": 45,
            "email": "dave.wilson@email.com",
            "phone": "+44 7700 900789",
            "preferred_language": "English",
            "category": "Digital-first self-serve",
            "category_reasoning": [
                "45 logins per month - power user",
                "Age 32 in core digital demographic",
                "£50,000 balance - premium customer"
            ],
            "upsell_eligible": True,
            "upsell_eligibility_reasoning": "Premium customer with high engagement",
            "upsell_products": ["Wealth Management", "Premium Credit Card", "Investment ISA"],
            "financial_indicators": {
                "account_health": "excellent",
                "engagement_level": "very_high",
                "digital_maturity": "expert"
            },
            "support_needs": [],
            "preferred_channels": ["in_app", "video_message", "email"],
            "risk_factors": []
        }
    ],
    "aggregates": {
        "total_customers": 3,
        "categories": {
            "Digital-first self-serve": 2,
            "Vulnerable / extra-support": 1
        },
        "upsell_eligible_count": 2,
        "vulnerable_count": 1,
        "accessibility_needs_count": 1,
        "insights": [
            "67% of customers are digital-first - prioritize app features",
            "33% require vulnerable customer protection",
            "67% eligible for upsell opportunities"
        ]
    },
    "segment_summaries": [
        {
            "segment": "Digital-first self-serve",
            "size": 2,
            "description": "Comfortable with apps and email; quick to act",
            "opportunities": ["In-app nudges", "Voice notes", "Video messages"]
        },
        {
            "segment": "Vulnerable / extra-support",
            "size": 1,
            "description": "Needs softer tone and extra care",
            "opportunities": ["Proactive callbacks", "No sales pressure"]
        }
    ],
    "analysis_metadata": {
        "total_analyzed": 3,
        "batch_size_used": 3,
        "api_model": "claude-3-5-sonnet-20241022",
        "analyzed_date": datetime.now().isoformat()
    }
}

def create_test_dataset():
    """Create the test dataset file."""
    
    # Save to data directory
    output_dir = Path("data/test_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "test_customers_analyzed.json"
    
    # Write the test data
    with open(output_file, 'w') as f:
        json.dump(TEST_CUSTOMERS, f, indent=2, default=str)
    
    print("✅ Test dataset created successfully!")
    print(f"📁 Saved to: {output_file}")
    print("\nTest customers:")
    print("1. Maria Garcia - Spanish, £25k (tests language + video)")
    print("2. Vulnerable Vera - Age 78 (tests protection rules)")
    print("3. Digital Dave - £50k (tests premium + video)")
    
    return output_file

def load_test_dataset():
    """Load the test dataset."""
    test_file = Path("data/test_data/test_customers_analyzed.json")
    
    if not test_file.exists():
        print("Test dataset not found, creating it...")
        create_test_dataset()
    
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    # Create the test dataset
    create_test_dataset()
    
    # Test loading it
    print("\nTesting load...")
    data = load_test_dataset()
    print(f"✅ Loaded {len(data['customer_categories'])} test customers")