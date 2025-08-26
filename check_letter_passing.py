"""
Check what letter content is actually being passed to Claude
"""

import sys
from pathlib import Path
sys.path.append('src')

def check_what_claude_receives():
    """See exactly what prompt Claude is getting."""
    
    print("=" * 60)
    print("CHECKING WHAT CLAUDE ACTUALLY RECEIVES")
    print("=" * 60)
    
    # Sample letter about money tools
    actual_letter = """
    Simple ways to stay on top of your everyday finances
    At [Bank Name], we're here to support you with helpful tools:
    - Set your own spending limits
    - Get real-time alerts
    - Track your savings goals
    Visit bankname.co.uk/moneytools to explore all features.
    """
    
    # Vulnerable Vera
    vera = {
        "customer_id": "CUST002",
        "name": "Vulnerable Vera",
        "age": 78,
        "category": "Vulnerable / extra-support",
        "preferred_language": "English"
    }
    
    print("\n📄 LETTER CONTENT TO REWRITE:")
    print("-" * 40)
    print(actual_letter)
    print("-" * 40)
    
    print("\n👤 CUSTOMER: Vera (Vulnerable)")
    
    # Build the EXACT prompt that would be sent
    prompt = f"""
    ORIGINAL LETTER TO REWRITE:
    ========================================
    {actual_letter}
    ========================================
    
    TASK: Rewrite this letter for this specific customer across multiple channels.
    Keep the same core information but make it completely personalized.
    
    CUSTOMER PROFILE:
    - Name: {vera['name']}
    - Age: {vera['age']}
    - Category: {vera['category']}
    
    REQUIREMENTS:
    1. Rewrite the letter content for each channel
    2. Keep the SAME INFORMATION about money management tools
    3. Adapt tone for vulnerable customer
    4. DON'T change the core message
    
    The letter is about: spending limits, alerts, savings goals
    You must include these same features in your rewrite!
    """
    
    print("\n📝 THIS IS THE PROMPT CLAUDE GETS:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    
    print("\n❌ THE PROBLEM:")
    print("Claude is probably ignoring the 'Keep the same information' instruction")
    print("and just generating generic vulnerable customer content!")
    
    return prompt

def show_the_fix_needed():
    """Show what needs to be fixed."""
    
    print("\n" + "=" * 60)
    print("WHAT NEEDS FIXING")
    print("=" * 60)
    
    print("""
    The prompt to Claude needs to be MORE EXPLICIT:
    
    ❌ Current: "Keep the same core information"
    ✅ Needed: "You MUST mention ALL of these topics from the original letter:
               - Setting spending limits
               - Real-time alerts  
               - Tracking savings goals
               - Website moneytools link
               DO NOT replace with generic support messages!"
    
    The system is being too "creative" and replacing content
    instead of rewriting it!
    """)

if __name__ == "__main__":
    check_what_claude_receives()
    show_the_fix_needed()