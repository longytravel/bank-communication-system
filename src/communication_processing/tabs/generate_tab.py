"""
Generate Tab Module - WITH REAL AI GENERATION
Handles the generation of communication plans using Claude or templates.
"""

import streamlit as st
from pathlib import Path
import sys
import time
import json
from datetime import datetime
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from communication_processing.cost_configuration import CostConfigurationManager
from business_rules.video_rules import VideoEligibilityRules

def render_generate_plans_tab():
    """Render the generate plans tab."""
    
    st.markdown("### Generate Communication Plans")
    
    # Check for customers in multiple places
    customer_categories = None
    
    # First check if customer_categories exists directly
    if 'customer_categories' in st.session_state:
        customer_categories = st.session_state.customer_categories
    # Otherwise check in analysis_results
    elif 'analysis_results' in st.session_state and st.session_state.analysis_results:
        customer_categories = st.session_state.analysis_results.get('customer_categories', [])
    
    # If no customers found, show warning
    if not customer_categories:
        st.warning("Please load customers first (use the test customers button or run Customer Analysis)")
        return
        
    if 'selected_letter' not in st.session_state:
        st.warning("Please select a letter from the Letter Management page first.")
        return
    
    # Now we have customers, continue with the rest
    selected_letter = st.session_state.selected_letter
    
    # Customer selection options
    st.markdown("#### Select Customers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        filter_option = st.selectbox(
            "Customer Selection",
            ["All Customers", "First 20", "First 10", "First 5"],
            help="Choose how many customers to process"
        )
    
    with col2:
        processing_mode = st.selectbox(
            "Processing Mode",
            ["Demo Generation (Fast)", "Full AI Generation (Uses Claude)"],
            help="Demo uses templates (instant), Full AI calls Claude API (slower but personalized)"
        )
    
    # Filter customers based on selection
    filtered_customers = filter_customers(customer_categories, filter_option)
    
    st.info(f"Will generate plans for {len(filtered_customers)} customers")
    
    # Channel options
    st.markdown("#### Channel Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    options = {}
    with col1:
        options['enable_sms'] = st.checkbox("Enable SMS", value=True)
    with col2:
        options['enable_email'] = st.checkbox("Enable Email", value=True)
    with col3:
        options['enable_voice'] = st.checkbox("Enable Voice Notes", value=False)
    with col4:
        options['enable_video'] = st.checkbox("Enable Video Messages", value=True)
    
    # Generation button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        button_text = "Generate with Claude AI" if processing_mode == "Full AI Generation (Uses Claude)" else "Generate Demo Plans"
        if st.button(
            f"{button_text} ({len(filtered_customers)} customers)",
            type="primary",
            use_container_width=True
        ):
            if processing_mode == "Full AI Generation (Uses Claude)":
                # ACTUALLY use AI generation
                generate_ai_communication_plans(filtered_customers, selected_letter, options)
            else:
                # Use demo/template generation (fast)
                generate_demo_communication_plans(filtered_customers, selected_letter, options)
    
    # Show results if generated
    if 'communication_plans_generated' in st.session_state:
        show_generation_success()

def generate_ai_communication_plans(customers, letter, options):
    """Generate REAL AI plans using Claude API."""
    
    st.markdown("""
    <div style="background: #7C3AED; color: white; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">AI Generation with Claude</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            Creating REAL personalized content using Claude AI. This takes 2-3 seconds per customer...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = st.progress(0)
    status = st.empty()
    
    # Initialize managers
    cost_manager = CostConfigurationManager()
    
    try:
        from api.api_manager import APIManager
        api_manager = APIManager()
        
        if not api_manager.claude:
            st.error("Claude API not configured! Check your API key in config.py. Using demo mode instead.")
            generate_demo_communication_plans(customers, letter, options)
            return
    except Exception as e:
        st.error(f"Could not initialize API: {e}. Check your ANTHROPIC_API_KEY in config.py")
        generate_demo_communication_plans(customers, letter, options)
        return
    
    # Process all customers with REAL AI
    all_customer_plans = []
    
    for i, customer in enumerate(customers):
        status.text(f"Calling Claude API for {customer.get('name', 'Unknown')}...")
        progress.progress((i + 1) / len(customers))
        
        # Generate REAL AI content
        classification_type = letter.get('classification', {}).get('classification', 'INFORMATION')
        
        try:
            # Build detailed prompt for Claude
            prompt = f"""
            Create personalized banking communication content for this customer.
            
            CUSTOMER DETAILS:
            - Name: {customer.get('name')}
            - Category: {customer.get('category')}
            - Balance: £{customer.get('account_balance', 0):,}
            - Age: {customer.get('age')}
            - Digital Maturity: {customer.get('financial_indicators', {}).get('digital_maturity', 'unknown')}
            - Communication Type: {classification_type}
            
            Generate personalized content for these channels:
            - Email (subject and body)
            - SMS (max 160 characters)  
            - Letter (greeting, body, closing)
            - In-app notification (title and message)
            
            Make the content:
            1. Personal and appropriate for their customer category
            2. Match the tone for {classification_type} communication
            3. Be specific to their profile (not generic)
            
            Return ONLY a JSON object with this structure:
            {{
                "email": {{
                    "subject": "personalized subject",
                    "body": "personalized email body"
                }},
                "sms": {{
                    "text": "SMS text max 160 chars"
                }},
                "letter": {{
                    "greeting": "Dear [Name]",
                    "body": "letter body text",
                    "closing": "Yours sincerely"
                }},
                "in_app": {{
                    "push_title": "Resonance Bank",
                    "push_body": "short push notification",
                    "message_subject": "in-app subject",
                    "message_body": "full in-app message"
                }}
            }}
            """
            
            # Actually call Claude API
            status.text(f"Claude is generating content for {customer.get('name')}... (API call in progress)")
            
            response = api_manager.claude._with_exponential_backoff(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse Claude's response
            content_text = response.content[0].text
            
            # Clean JSON if wrapped in markdown
            if "```json" in content_text:
                content_text = content_text.split("```json")[1].split("```")[0]
            elif "```" in content_text:
                content_text = content_text.split("```")[1].split("```")[0]
            
            ai_content = json.loads(content_text.strip())
            
            # Build the plan with AI content
            channels = get_channels_for_category(customer.get('category'), classification_type, customer, options)
            costs = calculate_channel_costs(channels, cost_manager)
            
            customer_plan = {
                'customer_id': customer.get('customer_id', 'Unknown'),
                'customer_name': customer.get('name'),
                'customer_category': customer.get('category'),
                'classification_type': classification_type,
                'channels': channels,
                'content': ai_content,
                'costs': costs,
                'upsell_eligible': customer.get('upsell_eligible', False),
                'ai_generated': True,
                'generation_method': 'Claude AI'
            }
            
            all_customer_plans.append(customer_plan)
            
            # Rate limit delay
            time.sleep(2)  # 2 second delay between API calls
            
        except json.JSONDecodeError as e:
            st.warning(f"Claude response parsing failed for {customer.get('name')}: {e}")
            # Fallback to template
            customer_plan = create_demo_content_for_customer(customer, classification_type, cost_manager, options)
            customer_plan['generation_method'] = 'Template (AI failed)'
            all_customer_plans.append(customer_plan)
            
        except Exception as e:
            st.warning(f"AI generation failed for {customer.get('name')}: {str(e)[:100]}")
            # Fallback to template
            customer_plan = create_demo_content_for_customer(customer, classification_type, cost_manager, options)
            customer_plan['generation_method'] = 'Template (API error)'
            all_customer_plans.append(customer_plan)
    
    status.text("AI generation complete!")
    progress.progress(1.0)
    time.sleep(1)
    
    # Store all generated plans
    st.session_state.communication_plans_generated = True
    st.session_state.all_customer_plans = all_customer_plans
    st.session_state.generated_plans_data = {
        'customers': customers,
        'letter': letter,
        'options': options,
        'generated_at': datetime.now(),
        'all_plans': all_customer_plans,
        'ai_generated': True
    }
    
    # Clear progress
    progress.empty()
    status.empty()
    
    st.success(f"Generated REAL AI-powered plans for {len(customers)} customers using Claude!")
    st.balloons()
    st.rerun()

def generate_demo_communication_plans(customers, letter, options):
    """Generate demo plans using templates (fast, no API calls)."""
    
    st.markdown("""
    <div style="background: #3B82F6; color: white; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">Generating Demo Plans</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            Creating template-based demo content (no API calls)...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = st.progress(0)
    status = st.empty()
    
    # Initialize cost manager
    cost_manager = CostConfigurationManager()
    
    # Process all customers and ACTUALLY CREATE PLANS
    all_customer_plans = []
    
    for i, customer in enumerate(customers):
        status.text(f"Processing customer {i+1} of {len(customers)}: {customer.get('name', 'Unknown')}...")
        progress.progress((i + 1) / len(customers))
        
        # Generate demo content for this customer
        classification_type = letter.get('classification', {}).get('classification', 'INFORMATION')
        customer_plan = create_demo_content_for_customer(customer, classification_type, cost_manager, options)
        customer_plan['generation_method'] = 'Template'
        all_customer_plans.append(customer_plan)
        
        time.sleep(0.1)  # Small delay for visual effect
    
    status.text("All plans generated successfully!")
    progress.progress(1.0)
    time.sleep(1)
    
    # Store all generated plans (WITH ACTUAL DATA!)
    st.session_state.communication_plans_generated = True
    st.session_state.all_customer_plans = all_customer_plans
    st.session_state.generated_plans_data = {
        'customers': customers,
        'letter': letter,
        'options': options,
        'generated_at': datetime.now(),
        'all_plans': all_customer_plans,
        'ai_generated': False
    }
    
    # Clear progress
    progress.empty()
    status.empty()
    
    st.success(f"Generated template-based plans for {len(customers)} customers!")
    st.rerun()

def filter_customers(customer_categories: List[Dict], filter_option: str) -> List[Dict]:
    """Filter customers based on selection."""
    if filter_option == "First 20":
        return customer_categories[:20]
    elif filter_option == "First 10":
        return customer_categories[:10]
    elif filter_option == "First 5":
        return customer_categories[:5]
    else:
        return customer_categories

def create_demo_content_for_customer(customer: Dict, classification_type: str, cost_manager, options: Dict) -> Dict:
    """Create demo content for a single customer using templates."""
    
    name = customer.get('name', 'Customer')
    category = customer.get('category', 'Unknown')
    upsell_eligible = customer.get('upsell_eligible', False)
    
    # Check video eligibility
    video_rules = VideoEligibilityRules()
    video_eligibility = video_rules.is_video_eligible(customer, classification_type)
    
    # Determine channels based on category
    channels = get_channels_for_category(category, classification_type, customer, options)
    
    # Generate template content
    content = generate_template_content(name, category, classification_type, upsell_eligible, customer, options)
    
    # Calculate costs
    costs = calculate_channel_costs(channels, cost_manager)
    
    return {
        'customer_id': customer.get('customer_id', 'Unknown'),
        'customer_name': name,
        'customer_category': category,
        'classification_type': classification_type,
        'channels': channels,
        'content': content,
        'costs': costs,
        'upsell_eligible': upsell_eligible,
        'video_eligible': video_eligibility.get('eligible', False),
        'video_tier': video_eligibility.get('tier'),
        'video_score': video_eligibility.get('score', 0)
    }

def get_channels_for_category(category: str, classification_type: str, customer: Dict = None, options: Dict = None) -> List[str]:
    """Determine appropriate channels based on customer category."""
    
    channels = []
    
    # Category-based channel selection
    if category == "Digital-first self-serve":
        channels = ['in_app', 'email']
        if options and options.get('enable_sms'):
            channels.append('sms')
    elif category == "Premium relationship-managed":
        channels = ['email', 'letter']
        if options and options.get('enable_voice'):
            channels.append('voice_note')
        # Check for video eligibility
        video_rules = VideoEligibilityRules()
        if customer and options and options.get('enable_video'):
            video_eligibility = video_rules.is_video_eligible(customer, classification_type)
            if video_eligibility.get('eligible'):
                channels.append('video_message')
    elif category == "Protected" or category == "Vulnerable / extra-support":
        channels = ['letter']  # Always use letter for protected customers
    elif category == "Traditional branch-based":
        channels = ['letter', 'email']
    else:  # Cost-conscious automated
        channels = ['email']
        if options and options.get('enable_sms'):
            channels.append('sms')
    
    return channels

def calculate_channel_costs(channels: List[str], cost_manager) -> Dict:
    """Calculate costs for selected channels."""
    
    costs = {
        'traditional_total': 2.50,  # Assume all letters cost
        'optimized_total': 0.0,
        'channels': {},  # FIXED: Changed from 'channel_breakdown' to 'channels'
        'savings': 0,
        'savings_percentage': 0
    }
    
    # Calculate optimized costs
    channel_costs = {
        'in_app': 0.002,
        'email': 0.01,
        'sms': 0.05,
        'letter': 2.50,
        'voice_note': 0.15,
        'video_message': 0.25
    }
    
    for channel in channels:
        cost = channel_costs.get(channel, 0.001)
        costs['channels'][channel] = {
            'cost': cost,
            'carbon_g': 0.1
        }
        costs['optimized_total'] += cost
    
    costs['savings'] = costs['traditional_total'] - costs['optimized_total']
    costs['savings_percentage'] = (costs['savings'] / costs['traditional_total'] * 100) if costs['traditional_total'] > 0 else 0
    
    return costs

def generate_template_content(name: str, category: str, classification_type: str, 
                             upsell_eligible: bool, customer: Dict, options: Dict) -> Dict:
    """Generate template content for demo purposes."""
    
    content = {}
    
    # In-app notification
    content['in_app'] = {
        'push_title': 'Resonance Bank',
        'push_body': f'Important update for you, {name}',
        'message_subject': f'{classification_type}: Action Required',
        'message_body': f'Dear {name}, we have an important update regarding your account. Please review at your convenience.',
        'cta_primary': 'View Details',
        'cta_secondary': 'Remind Me Later'
    }
    
    # Email
    content['email'] = {
        'subject': f'Important: {classification_type} - Action Required',
        'preview': f'Dear {name}, important information about your account',
        'body': f'Dear {name},\n\nWe have important information regarding your Resonance Bank account. As a valued {category} customer, we wanted to ensure you receive this update promptly.\n\nPlease log in to your account to review the details.\n\nBest regards,\nResonance Bank Team'
    }
    
    # SMS
    content['sms'] = {
        'text': f'Resonance Bank: Hi {name}, important account update. Check your app or call us. Ref: {classification_type[:3].upper()}'
    }
    
    # Letter
    content['letter'] = {
        'greeting': f'Dear {name}',
        'body': f'We are writing to inform you about an important matter regarding your account. As a {category} customer, we value your relationship with Resonance Bank.',
        'closing': 'Yours sincerely'
    }
    
    # Voice note
    content['voice_note'] = {
        'script': f'Hello {name}, this is Resonance Bank with an important account update. Please check your secure messages or visit your nearest branch.'
    }
    
    # Video message (for eligible customers)
    if customer.get('account_balance', 0) > 25000:
        content['video_message'] = {
            'script': f'Hello {name}, I\'m your relationship manager at Resonance Bank. I wanted to personally reach out about an important update to your account.',
            'greeting': f'Good day, {name}',
            'closing': 'Thank you for being a valued customer'
        }
    
    # Upsell message
    if upsell_eligible:
        upsell_products = customer.get('upsell_products', [])
        if upsell_products:
            content['upsell_message'] = f"Based on your profile, you may be interested in: {', '.join(upsell_products)}"
    
    return content

def show_generation_success():
    """Show generation success message."""
    st.markdown("""
    <div style="background: #10B981; color: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">Generation Complete!</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            All customer communication plans have been created. Go to the "Results" tab to view them.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("View Results", use_container_width=True):
            pass  # Will switch to results tab on rerun
    
    with col2:
        if st.button("Generate New Plans", use_container_width=True, type="secondary"):
            if 'communication_plans_generated' in st.session_state:
                del st.session_state.communication_plans_generated
            if 'generated_plans_data' in st.session_state:
                del st.session_state.generated_plans_data
            if 'all_customer_plans' in st.session_state:
                del st.session_state.all_customer_plans
            st.rerun()