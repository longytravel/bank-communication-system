"""
Script to update customer CSV with Polish and Urdu high-value customers
Ensures they qualify for video messages based on system rules
"""

import pandas as pd
from pathlib import Path
import random

def update_customer_data_for_multilingual_testing():
    """
    Update customer data CSV to include Polish and Urdu customers
    who qualify for video messages (high-value, digitally engaged).
    """
    
    # Load existing CSV
    csv_path = Path("data/customer_profiles/sample_customers.csv")
    
    # Check if file exists
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        print("Creating sample data instead...")
        df = create_sample_data()
    else:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded existing CSV with {len(df)} customers")
    
    # Ensure we have required columns
    required_columns = [
        'customer_id', 'name', 'age', 'account_balance', 
        'digital_logins_per_month', 'preferred_language'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            if col == 'preferred_language':
                df[col] = 'English'  # Default to English
            elif col == 'digital_logins_per_month':
                df[col] = 5  # Default value
            else:
                print(f"⚠️ Warning: Missing column {col}")
    
    # VIDEO ELIGIBILITY RULES FROM YOUR SYSTEM:
    # - Minimum £10,000 balance
    # - Minimum 10 digital logins per month
    # - Age between 25-65
    # - Not vulnerable (category != 'Vulnerable / extra-support')
    
    # CUSTOMER 1: Polish High-Value Customer
    # Find a suitable customer to convert (preferably already high-value)
    polish_index = 0  # First customer
    if len(df) > 5:
        # Look for existing high-value customer
        high_value = df[df['account_balance'] >= 10000]
        if not high_value.empty:
            polish_index = high_value.index[0]
    
    # Update to Polish high-value customer
    df.loc[polish_index, 'name'] = 'Stanisław Kowalski'
    df.loc[polish_index, 'preferred_language'] = 'Polish'
    df.loc[polish_index, 'account_balance'] = 25000  # £25k - well above threshold
    df.loc[polish_index, 'age'] = 42  # Perfect age range
    df.loc[polish_index, 'digital_logins_per_month'] = 18  # High digital engagement
    df.loc[polish_index, 'mobile_app_usage'] = 'high'
    df.loc[polish_index, 'email_opens_per_month'] = 12
    df.loc[polish_index, 'employment_status'] = 'Employed'
    df.loc[polish_index, 'income_level'] = 'High'
    df.loc[polish_index, 'prefers_digital'] = True
    df.loc[polish_index, 'requires_support'] = False
    df.loc[polish_index, 'branch_visits_per_month'] = 0
    df.loc[polish_index, 'phone_calls_per_month'] = 0
    
    print(f"✅ Updated customer {polish_index}: Stanisław Kowalski (Polish, £25k, Video-eligible)")
    
    # CUSTOMER 2: Urdu High-Value Customer  
    # Find another customer to convert
    urdu_index = 1  # Second customer
    if len(df) > 10:
        # Find another high-value candidate
        candidates = df[(df['account_balance'] >= 5000) & (df.index != polish_index)]
        if not candidates.empty:
            urdu_index = candidates.index[0]
    
    # Update to Urdu high-value customer
    df.loc[urdu_index, 'name'] = 'Ahmed Hassan'
    df.loc[urdu_index, 'preferred_language'] = 'Urdu'
    df.loc[urdu_index, 'account_balance'] = 35000  # £35k - premium customer
    df.loc[urdu_index, 'age'] = 38  # Perfect age range
    df.loc[urdu_index, 'digital_logins_per_month'] = 22  # Very high digital engagement
    df.loc[urdu_index, 'mobile_app_usage'] = 'high'
    df.loc[urdu_index, 'email_opens_per_month'] = 15
    df.loc[urdu_index, 'employment_status'] = 'Business Owner'
    df.loc[urdu_index, 'income_level'] = 'Very High'
    df.loc[urdu_index, 'prefers_digital'] = True
    df.loc[urdu_index, 'requires_support'] = False
    df.loc[urdu_index, 'branch_visits_per_month'] = 1
    df.loc[urdu_index, 'phone_calls_per_month'] = 0
    
    print(f"✅ Updated customer {urdu_index}: Ahmed Hassan (Urdu, £35k, Video-eligible)")
    
    # CUSTOMER 3: Add another Polish customer (mid-value)
    if len(df) > 2:
        polish2_index = 2
        df.loc[polish2_index, 'name'] = 'Anna Nowak'
        df.loc[polish2_index, 'preferred_language'] = 'Polish'
        df.loc[polish2_index, 'account_balance'] = 15000  # £15k - still video eligible
        df.loc[polish2_index, 'age'] = 35
        df.loc[polish2_index, 'digital_logins_per_month'] = 14
        df.loc[polish2_index, 'mobile_app_usage'] = 'medium'
        df.loc[polish2_index, 'email_opens_per_month'] = 8
        df.loc[polish2_index, 'employment_status'] = 'Employed'
        df.loc[polish2_index, 'income_level'] = 'Medium'
        df.loc[polish2_index, 'prefers_digital'] = True
        df.loc[polish2_index, 'requires_support'] = False
        
        print(f"✅ Updated customer {polish2_index}: Anna Nowak (Polish, £15k, Video-eligible)")
    
    # Save the updated CSV
    output_path = Path("data/customer_profiles/sample_customers_multilingual.csv")
    df.to_csv(output_path, index=False)
    print(f"\n📁 Saved updated CSV to: {output_path}")
    
    # Print video eligibility check
    print("\n🎬 Video Eligibility Check:")
    print("-" * 50)
    
    video_eligible_customers = []
    for idx in [polish_index, urdu_index, 2]:
        if idx < len(df):
            customer = df.iloc[idx]
            check_video_eligibility(customer, video_eligible_customers)
    
    # Summary statistics
    print("\n📊 Summary:")
    print("-" * 50)
    print(f"Total customers: {len(df)}")
    print(f"Polish customers: {len(df[df['preferred_language'] == 'Polish'])}")
    print(f"Urdu customers: {len(df[df['preferred_language'] == 'Urdu'])}")
    print(f"Video-eligible customers: {len(video_eligible_customers)}")
    print(f"High-value (£10k+): {len(df[df['account_balance'] >= 10000])}")
    
    return df

def check_video_eligibility(customer, eligible_list):
    """Check if customer meets video eligibility criteria."""
    name = customer['name']
    balance = customer.get('account_balance', 0)
    age = customer.get('age', 0)
    logins = customer.get('digital_logins_per_month', 0)
    language = customer.get('preferred_language', 'English')
    
    # Video eligibility rules
    is_eligible = (
        balance >= 10000 and  # £10k minimum
        logins >= 10 and      # 10+ logins per month
        25 <= age <= 65       # Age range
    )
    
    status = "✅ ELIGIBLE" if is_eligible else "❌ NOT ELIGIBLE"
    print(f"{status} - {name} ({language})")
    print(f"  Balance: £{balance:,} {'✓' if balance >= 10000 else '✗'}")
    print(f"  Age: {age} {'✓' if 25 <= age <= 65 else '✗'}")
    print(f"  Digital logins: {logins}/month {'✓' if logins >= 10 else '✗'}")
    
    if is_eligible:
        eligible_list.append(name)
    
    return is_eligible

def create_sample_data():
    """Create sample data if CSV doesn't exist."""
    data = {
        'customer_id': [f'CUST{i:03d}' for i in range(1, 21)],
        'name': [f'Customer {i}' for i in range(1, 21)],
        'age': [random.randint(25, 75) for _ in range(20)],
        'account_balance': [random.randint(1000, 50000) for _ in range(20)],
        'digital_logins_per_month': [random.randint(0, 30) for _ in range(20)],
        'mobile_app_usage': [random.choice(['high', 'medium', 'low']) for _ in range(20)],
        'email_opens_per_month': [random.randint(0, 20) for _ in range(20)],
        'phone_calls_per_month': [random.randint(0, 5) for _ in range(20)],
        'branch_visits_per_month': [random.randint(0, 3) for _ in range(20)],
        'prefers_digital': [random.choice([True, False]) for _ in range(20)],
        'requires_support': [random.choice([True, False]) for _ in range(20)],
        'accessibility_needs': [False] * 20,
        'employment_status': [random.choice(['Employed', 'Self-employed', 'Retired']) for _ in range(20)],
        'income_level': [random.choice(['Low', 'Medium', 'High']) for _ in range(20)],
        'preferred_language': ['English'] * 20
    }
    return pd.DataFrame(data)

# Run the update
if __name__ == "__main__":
    print("🚀 Starting Customer Data Update for Multilingual Testing")
    print("=" * 60)
    update_customer_data_for_multilingual_testing()
    print("\n✅ Update complete! Use 'sample_customers_multilingual.csv' in your system.")