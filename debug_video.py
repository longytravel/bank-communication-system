"""
Debug why Maria isn't getting video generation
"""

import sys
sys.path.append('src')

from business_rules.video_rules import VideoEligibilityRules

# Maria's actual data from your CSV
maria_data = {
    'customer_id': 'CUST011',
    'name': 'Maria Garcia',
    'age': 35,
    'account_balance': 25000,  # This should qualify her!
    'digital_logins_per_month': 18,  # Good digital engagement
    'category': 'Digital-first self-serve',  # Right category
    'preferred_language': 'Spanish',
    'upsell_eligible': True,
    'financial_indicators': {
        'account_health': 'healthy',
        'engagement_level': 'high',
        'digital_maturity': 'advanced'
    }
}

print("=" * 60)
print("MARIA'S VIDEO ELIGIBILITY CHECK")
print("=" * 60)

# Check video eligibility
video_rules = VideoEligibilityRules()
eligibility = video_rules.is_video_eligible(maria_data, 'INFORMATION')

print(f"\n1. Maria's Data:")
print(f"   Name: {maria_data['name']}")
print(f"   Balance: £{maria_data['account_balance']:,}")
print(f"   Category: {maria_data['category']}")
print(f"   Digital Logins: {maria_data['digital_logins_per_month']}/month")
print(f"   Age: {maria_data['age']}")

print(f"\n2. Video Eligibility Result:")
print(f"   Eligible: {eligibility['eligible']}")
print(f"   Score: {eligibility['score']}/100")
print(f"   Tier: {eligibility.get('tier', 'None')}")

print(f"\n3. Scoring Breakdown:")
for reason in eligibility['reasons']:
    print(f"   - {reason}")

print(f"\n4. Expected Result:")
print(f"   Maria SHOULD be eligible because:")
print(f"   - She's Digital-first (40 points)")
print(f"   - Has £25,000 balance - GOLD tier (25 points)")
print(f"   - Has 18 logins/month (10+ points)")
print(f"   - Age 35 is in prime range (10 points)")
print(f"   - Total should be ~85 points (well above 50 threshold)")

if not eligibility['eligible']:
    print(f"\n❌ PROBLEM DETECTED!")
    print(f"   Maria should be eligible but isn't.")
    print(f"   Check the video_rules.py file for issues.")
else:
    print(f"\n✅ Maria IS eligible for video!")
    print(f"   The issue must be in the video generation step.")

print("=" * 60)