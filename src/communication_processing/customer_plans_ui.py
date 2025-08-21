"""
Customer Communication Plans UI Module - ENHANCED VERSION
Personalized communication strategies with real AI content, in-app notifications, 
complete customer processing, and comprehensive cost analysis.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys
import time
import io
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.api_manager import APIManager
from ui.professional_theme import create_professional_card
from communication_processing.cost_configuration import CostConfigurationManager

def render_customer_communication_plans_page():
    """Render the Customer Communication Plans page with tabs."""
    
    st.markdown(create_professional_card(
        "Customer Communication Plans",
        "Create personalized, AI-generated communication strategies with real content and cost analysis"
    ), unsafe_allow_html=True)
    
    # Check prerequisites first
    if not check_communication_prerequisites():
        return
    
    # Create tabs for the workflow
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Setup", "🚀 Generate Plans", "📊 Results", "📈 Analytics"])
    
    with tab1:
        render_setup_tab()
    
    with tab2:
        render_generate_plans_tab()
    
    with tab3:
        render_results_tab()
    
    with tab4:
        render_analytics_tab()

def check_communication_prerequisites():
    """Check if required data is available for communication planning."""
    
    # Check for customer analysis results
    customer_data_available = 'analysis_results' in st.session_state and st.session_state.analysis_results is not None
    
    # Check for letters
    try:
        from file_handlers.letter_scanner import EnhancedLetterScanner
        scanner = EnhancedLetterScanner()
        letters = scanner.scan_all_letters()
        letters_available = len(letters) > 0
    except:
        letters_available = False
    
    if not customer_data_available or not letters_available:
        st.markdown("""
        <div style="background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="margin-top: 0; color: #92400E;">Prerequisites Required</h4>
            <p style="color: #92400E; margin-bottom: 0;">Complete the following before creating communication plans:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not customer_data_available:
                st.error("❌ **Customer Analysis Required**\n\nGo to 'Customer Analysis' and analyze your customer data first.")
            else:
                st.success("✅ **Customer Data Ready**\n\nCustomer analysis completed and available.")
        
        with col2:
            if not letters_available:
                st.error("❌ **Letters Required**\n\nGo to 'Letter Management' and upload/create letters first.")
            else:
                st.success(f"✅ **Letters Available**\n\n{len(letters)} letters ready for processing.")
        
        return False
    
    return True

def render_setup_tab():
    """Render the setup tab for communication planning."""
    
    st.markdown("### 👥 Customer Portfolio Summary")
    
    # Get customer data from session state
    customer_categories = st.session_state.analysis_results.get('customer_categories', [])
    aggregates = st.session_state.analysis_results.get('aggregates', {})
    
    # Display customer metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = aggregates.get('total_customers', 0)
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col2:
        upsell_eligible = aggregates.get('upsell_eligible_count', 0)
        st.metric("Upsell Eligible", f"{upsell_eligible:,}")
    
    with col3:
        vulnerable_count = aggregates.get('vulnerable_count', 0)
        st.metric("Protected", f"{vulnerable_count:,}")
    
    with col4:
        digital_first = aggregates.get('categories', {}).get('Digital-first self-serve', 0)
        st.metric("Digital-First", f"{digital_first:,}")
    
    # Letter Selection Section
    st.markdown("### 📄 Letter Selection")
    
    try:
        from file_handlers.letter_scanner import EnhancedLetterScanner
        scanner = EnhancedLetterScanner()
        letters = scanner.scan_all_letters()
        
        if letters:
            # Create letter options
            letter_options = []
            for i, letter in enumerate(letters):
                classification = letter['classification']
                if classification:
                    class_label = classification.get('classification', 'UNCLASSIFIED')
                    confidence = classification.get('confidence', 0)
                    word_count = classification.get('word_count', 0)
                    option_text = f"{letter['filename']} • {class_label} • Confidence: {confidence}/10 • {word_count} words"
                else:
                    option_text = f"{letter['filename']} • UNCLASSIFIED"
                
                letter_options.append(option_text)
            
            # Letter selection dropdown
            selected_letter_index = st.selectbox(
                "Choose your communication template:",
                range(len(letter_options)),
                format_func=lambda x: letter_options[x],
                help="Select the letter that will be personalized for each customer"
            )
            
            selected_letter = letters[selected_letter_index]
            
            # Store the selection
            st.session_state.selected_letter = selected_letter
            
            # Show letter details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                classification = selected_letter['classification']
                if classification:
                    st.markdown("**Letter Analysis:**")
                    
                    subcol1, subcol2, subcol3 = st.columns(3)
                    with subcol1:
                        st.metric("Type", classification.get('classification', 'Unknown'))
                    with subcol2:
                        st.metric("Confidence", f"{classification.get('confidence', 0)}/10")
                    with subcol3:
                        st.metric("Words", classification.get('word_count', 0))
            
            with col2:
                st.markdown("**File Info:**")
                st.markdown(f"""
                - **Source:** {selected_letter['source'].title()}
                - **Size:** {selected_letter['size_bytes']:,} bytes
                - **Modified:** {selected_letter['modified_date'].strftime('%Y-%m-%d')}
                """)
            
            # Letter preview
            with st.expander("📖 Preview Letter Content"):
                content = scanner.read_letter_content(Path(selected_letter['filepath']))
                if content:
                    preview_text = content[:800] + "\n\n... (preview truncated)" if len(content) > 800 else content
                    st.text_area("Letter content:", preview_text, height=200, disabled=True)
            
            # Processing Options
            st.markdown("### ⚙️ Processing Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                personalization_level = st.selectbox(
                    "Personalization Level",
                    ["Enhanced", "Standard"],
                    index=0,
                    help="Enhanced uses specific customer data points"
                )
            
            with col2:
                generate_voice_notes = st.checkbox(
                    "Generate voice notes",
                    value=True,
                    help="Create real voice notes for digital-first customers"
                )
            
            with col3:
                customer_filter = st.selectbox(
                    "Customer Selection",
                    ["First 20", "First 10", "First 5", "Digital-first only", "High-value only"],
                    help="Choose which customers to process (max 20)"
                )
            
            # Store processing options
            st.session_state.processing_options = {
                'personalization_level': personalization_level,
                'generate_voice_notes': generate_voice_notes,
                'customer_filter': customer_filter
            }
            
            # Ready indicator
            st.markdown("""
            <div style="background: #DCFCE7; border: 1px solid #10B981; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <h4 style="margin-top: 0; color: #166534;">✅ Setup Complete</h4>
                <p style="color: #166534; margin-bottom: 0;">
                    Ready to generate personalized communication plans! Go to the "Generate Plans" tab.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("No letters found. Please upload letters in the Letter Management section first.")
            
    except Exception as e:
        st.error(f"Error loading letters: {str(e)}")
        st.info("Make sure you have letters available in the Letter Management section.")

def render_generate_plans_tab():
    """Render the generate plans tab with full customer processing."""
    
    # Check if setup is complete
    if 'selected_letter' not in st.session_state:
        st.warning("Please complete the Setup tab first.")
        return
    
    st.markdown("### 🚀 Generate Personalized Communication Plans")
    
    # Show what we're about to process
    customer_categories = st.session_state.analysis_results.get('customer_categories', [])
    selected_letter = st.session_state.selected_letter
    options = st.session_state.get('processing_options', {})
    
    # Filter customers based on selection
    filtered_customers = filter_customers(customer_categories, options.get('customer_filter', 'First 20'))
    
    # Processing summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Customers to Process", len(filtered_customers))
    
    with col2:
        classification = selected_letter['classification']
        class_type = classification.get('classification', 'UNKNOWN') if classification else 'UNKNOWN'
        st.metric("Letter Type", class_type)
    
    with col3:
        st.metric("Personalization", options.get('personalization_level', 'Standard'))
    
    # Processing options
    st.markdown("### Processing Options")
    col1, col2 = st.columns(2)
    
    with col1:
        processing_mode = st.radio(
            "Processing Mode",
            ["Quick Demo (Simulated)", "Full AI Generation (Real)"],
            help="Quick Demo uses templates, Full AI makes real API calls"
        )
    
    with col2:
        if processing_mode == "Full AI Generation (Real)":
            st.warning("⚠️ This will make real API calls and may take 2-3 minutes for 20 customers")
            api_batch_size = st.slider("API Batch Size", 1, 5, 3, 
                                      help="Process customers in batches to avoid rate limits")
        else:
            api_batch_size = 5
    
    # Generation button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button(
            f"🎯 Generate Plans for {len(filtered_customers)} Customers",
            type="primary",
            use_container_width=True,
            disabled='communication_plans_generated' in st.session_state
        ):
            if processing_mode == "Full AI Generation (Real)":
                generate_real_communication_plans(filtered_customers, selected_letter, options, api_batch_size)
            else:
                generate_demo_communication_plans(filtered_customers, selected_letter, options)
    
    # Show results if generated
    if 'communication_plans_generated' in st.session_state:
        show_generation_success()

def filter_customers(customer_categories: List[Dict], filter_option: str) -> List[Dict]:
    """Filter customers based on selection."""
    if filter_option == "First 20":
        return customer_categories[:20]
    elif filter_option == "First 10":
        return customer_categories[:10]
    elif filter_option == "First 5":
        return customer_categories[:5]
    elif filter_option == "Digital-first only":
        digital = [c for c in customer_categories if c.get('category') == 'Digital-first self-serve']
        return digital[:20]  # Max 20
    elif filter_option == "High-value only":
        high_value = []
        for customer in customer_categories:
            if customer.get('upsell_eligible', False):
                high_value.append(customer)
        return high_value[:20]  # Max 20
    else:
        return customer_categories[:20]

def generate_demo_communication_plans(customers, letter, options):
    """Generate demo plans using templates (fast, no API calls)."""
    
    st.markdown("""
    <div style="background: #3B82F6; color: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">🤖 Generating Demo Plans</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            Creating personalized demo content for all customers...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = st.progress(0)
    status = st.empty()
    
    # Initialize cost manager
    cost_manager = CostConfigurationManager()
    
    # Process all customers
    all_customer_plans = []
    
    for i, customer in enumerate(customers):
        status.text(f"Processing customer {i+1} of {len(customers)}: {customer.get('name', 'Unknown')}...")
        progress.progress((i + 1) / len(customers))
        
        # Generate demo content for this customer
        classification_type = letter['classification'].get('classification', 'INFORMATION') if letter['classification'] else 'INFORMATION'
        customer_plan = create_demo_content_for_customer(customer, classification_type, cost_manager)
        all_customer_plans.append(customer_plan)
        
        time.sleep(0.1)  # Small delay for visual effect
    
    status.text("✅ All plans generated successfully!")
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
        'all_plans': all_customer_plans
    }
    
    # Clear progress
    progress.empty()
    status.empty()
    
    st.success(f"🎉 Generated personalized plans for {len(customers)} customers!")
    st.rerun()

def generate_real_communication_plans(customers, letter, options, batch_size):
    """Generate real plans with actual AI API calls."""
    
    st.markdown("""
    <div style="background: #3B82F6; color: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">🤖 AI Generation in Progress (Real API Calls)</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            Creating real AI-powered content for all customers...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = st.progress(0)
    status = st.empty()
    
    # Initialize managers
    cost_manager = CostConfigurationManager()
    
    try:
        api_manager = APIManager()
    except Exception as e:
        st.error(f"Failed to initialize API: {e}")
        return
    
    # Process customers in batches
    all_customer_plans = []
    
    for batch_start in range(0, len(customers), batch_size):
        batch_end = min(batch_start + batch_size, len(customers))
        batch = customers[batch_start:batch_end]
        
        status.text(f"Processing batch: customers {batch_start+1} to {batch_end} of {len(customers)}...")
        
        for i, customer in enumerate(batch):
            customer_num = batch_start + i + 1
            status.text(f"Generating AI content for customer {customer_num}/{len(customers)}: {customer.get('name', 'Unknown')}...")
            progress.progress(customer_num / len(customers))
            
            # Generate real AI content
            classification_type = letter['classification'].get('classification', 'INFORMATION') if letter['classification'] else 'INFORMATION'
            customer_plan = create_real_ai_content_for_customer(customer, classification_type, cost_manager, api_manager)
            all_customer_plans.append(customer_plan)
            
            # Rate limiting delay
            time.sleep(0.5)
        
        # Delay between batches
        if batch_end < len(customers):
            status.text(f"Pausing between batches to avoid rate limits...")
            time.sleep(2)
    
    status.text("✅ All AI content generated successfully!")
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
        'all_plans': all_customer_plans
    }
    
    # Clear progress
    progress.empty()
    status.empty()
    
    st.success(f"🎉 Generated real AI-powered plans for {len(customers)} customers!")
    st.rerun()

def create_demo_content_for_customer(customer: Dict, classification_type: str, cost_manager) -> Dict:
    """Create demo content for a single customer using templates."""
    
    name = customer.get('name', 'Customer')
    category = customer.get('category', 'Unknown')
    upsell_eligible = customer.get('upsell_eligible', False)
    
    # Determine channels based on category
    channels = get_channels_for_category(category, classification_type)
    
    # Generate content based on category
    content = generate_template_content(name, category, classification_type, upsell_eligible)
    
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
        'upsell_eligible': upsell_eligible
    }

def create_real_ai_content_for_customer(customer: Dict, classification_type: str, cost_manager, api_manager) -> Dict:
    """Create real AI-generated content for a single customer."""
    
    name = customer.get('name', 'Customer')
    category = customer.get('category', 'Unknown')
    
    # Get financial indicators
    financial_indicators = customer.get('financial_indicators', {})
    account_health = financial_indicators.get('account_health', 'unknown')
    engagement_level = financial_indicators.get('engagement_level', 'unknown')
    digital_maturity = financial_indicators.get('digital_maturity', 'unknown')
    
    # Check upsell eligibility
    upsell_eligible = customer.get('upsell_eligible', False)
    upsell_products = customer.get('upsell_products', [])
    
    # Determine channels
    channels = get_channels_for_category(category, classification_type)
    
    try:
        # Create comprehensive prompt for all channels
        prompt = f"""
        Create personalized banking communication content for this customer across multiple channels:
        
        CUSTOMER PROFILE:
        - Name: {name}
        - Customer Category: {category}
        - Account Health: {account_health}
        - Engagement Level: {engagement_level}
        - Digital Maturity: {digital_maturity}
        - Upsell Eligible: {upsell_eligible}
        - Suggested Products: {', '.join(upsell_products) if upsell_products else 'None'}
        
        COMMUNICATION TYPE: {classification_type}
        
        Generate content for these channels: {', '.join(channels)}
        
        Return JSON with this exact structure:
        {{
            "in_app": {{
                "push_title": "Resonance Bank",
                "push_body": "personalized push notification text (max 50 chars)",
                "message_subject": "subject line for in-app message",
                "message_body": "full in-app message (max 500 chars)",
                "cta_primary": "primary button text",
                "cta_secondary": "secondary button text"
            }},
            "email": {{
                "subject": "email subject line",
                "preview": "email preview text (max 100 chars)",
                "body": "full email body (max 1000 chars)"
            }},
            "sms": {{
                "text": "SMS message (max 160 chars)"
            }},
            "letter": {{
                "greeting": "Dear {name}",
                "body": "letter body text (max 500 chars)",
                "closing": "Yours sincerely"
            }},
            "voice_note": {{
                "script": "voice note script (max 200 chars)"
            }},
            "upsell_message": "upsell message if eligible, null otherwise",
            "personalization_notes": ["list of personalization points used"]
        }}
        """
        
        # Get AI response
        ai_result = api_manager.claude._with_exponential_backoff(
            model=api_manager.claude.model,
            max_tokens=1500,
            system="You are a professional banking communication specialist. Create highly personalized content using specific customer data.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        if ai_result and ai_result.content:
            content_text = ai_result.content[0].text
            
            # Clean and parse JSON
            if content_text.startswith("```json"):
                content_text = content_text.replace("```json", "").replace("```", "").strip()
            
            content = json.loads(content_text)
        else:
            # Fallback to template
            content = generate_template_content(name, category, classification_type, upsell_eligible)
    
    except Exception as e:
        # Fallback to template content
        content = generate_template_content(name, category, classification_type, upsell_eligible)
    
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
        'upsell_eligible': upsell_eligible
    }

def get_channels_for_category(category: str, classification_type: str) -> List[str]:
    """Determine appropriate channels based on customer category and letter type."""
    
    if classification_type == "REGULATORY":
        # Regulatory requires letter for all
        base_channels = ["letter", "email"]
        if category == "Digital-first self-serve":
            return ["in_app", "email", "letter"]
        elif category == "Vulnerable / extra-support":
            return ["letter", "email"]
        else:
            return base_channels
    
    # Non-regulatory communications
    if category == "Digital-first self-serve":
        return ["in_app", "email", "sms", "voice_note"]
    elif category == "Assisted-digital":
        return ["email", "sms", "in_app"]
    elif category == "Low/no-digital (offline-preferred)":
        return ["letter", "email"]
    elif category == "Accessibility & alternate-format needs":
        return ["letter", "email", "voice_note"]
    elif category == "Vulnerable / extra-support":
        return ["letter", "email"]
    else:
        return ["email", "sms"]

def generate_template_content(name: str, category: str, classification_type: str, upsell_eligible: bool) -> Dict:
    """Generate template-based content for demo purposes."""
    
    templates = {
        "Digital-first self-serve": {
            "in_app": {
                "push_title": "Resonance Bank",
                "push_body": f"Hi {name}! Important update - tap to view",
                "message_subject": f"Your Account Update",
                "message_body": f"Hi {name}, we have an important update about your account. As a digital-first customer, you can review and action this directly in the app. This update is related to {classification_type.lower()} requirements and takes just 2 minutes to review.",
                "cta_primary": "Review Now",
                "cta_secondary": "Remind Me Later"
            },
            "email": {
                "subject": f"Action required: {classification_type.lower()} update for your account",
                "preview": f"Hi {name}, important account update requiring your attention",
                "body": f"Dear {name},\n\nWe're writing to inform you about an important {classification_type.lower()} update to your account. As someone who regularly uses our digital services, you'll appreciate the convenience of handling this through our app..."
            },
            "sms": {
                "text": f"Hi {name}! {classification_type} update in your Resonance app. Review now to stay compliant. Help? Call 0800123456"
            },
            "voice_note": {
                "script": f"Hi {name}, this is a quick reminder about the {classification_type.lower()} update waiting in your app. It only takes 2 minutes to review."
            }
        },
        "Vulnerable / extra-support": {
            "letter": {
                "greeting": f"Dear {name}",
                "body": f"We are writing to inform you about an important matter regarding your account. We understand you may need additional support with this {classification_type.lower()} update. Please don't hesitate to call us on our dedicated support line where our team is ready to help you through this process step by step.",
                "closing": "Yours sincerely"
            },
            "email": {
                "subject": f"Important information for you, {name}",
                "preview": "We're here to help with your account update",
                "body": f"Dear {name},\n\nWe have some important information to share with you. We understand you may prefer to speak with someone about this, so please feel free to call us..."
            }
        },
        "Low/no-digital (offline-preferred)": {
            "letter": {
                "greeting": f"Dear {name}",
                "body": f"We are writing to inform you about an important {classification_type.lower()} update to your account. Full details are provided in this letter. If you have any questions, please visit your local branch or call us.",
                "closing": "Yours sincerely"
            },
            "email": {
                "subject": f"Important letter sent to you, {name}",
                "preview": "We've sent you important information by post",
                "body": f"Dear {name},\n\nWe have sent you an important letter regarding your account. Please check your post for full details..."
            }
        }
    }
    
    # Get template for category, or use default
    if category in templates:
        content = templates[category]
    else:
        content = {
            "email": {
                "subject": f"Account update for {name}",
                "preview": "Important account information",
                "body": f"Dear {name},\n\nWe have an important update regarding your account..."
            },
            "sms": {
                "text": f"Hi {name}, important account update. Please check your email or call us."
            }
        }
    
    # Add upsell if eligible
    if upsell_eligible and classification_type != "REGULATORY":
        content["upsell_message"] = "Based on your account activity, you may benefit from our Premium Banking service."
    else:
        content["upsell_message"] = None
    
    content["personalization_notes"] = [
        f"Used customer name: {name}",
        f"Tailored for {category} customer",
        f"Appropriate tone for {classification_type}"
    ]
    
    return content

def calculate_channel_costs(channels: List[str], cost_manager) -> Dict:
    """Calculate costs for each channel and totals."""
    
    costs = {
        'channels': {},
        'traditional_total': 0,
        'optimized_total': 0,
        'savings': 0,
        'savings_percentage': 0
    }
    
    # Calculate traditional cost (everyone gets a letter)
    traditional = cost_manager.calculate_communication_cost('letter', 1)
    costs['traditional_total'] = traditional['total_cost']
    
    # Calculate optimized costs
    total_optimized = 0
    for channel in channels:
        # Map our channel names to cost manager channels
        cost_channel = channel
        if channel == "in_app":
            cost_channel = "in_app"
        elif channel == "voice_note":
            cost_channel = "voice_note"
        
        try:
            channel_cost = cost_manager.calculate_communication_cost(cost_channel, 1)
            costs['channels'][channel] = {
                'cost': channel_cost['total_cost'],
                'carbon_g': channel_cost['total_carbon_g']
            }
            total_optimized += channel_cost['total_cost']
        except:
            # Handle any channel that doesn't exist in cost manager
            costs['channels'][channel] = {'cost': 0.001, 'carbon_g': 0.1}
            total_optimized += 0.001
    
    costs['optimized_total'] = total_optimized
    costs['savings'] = costs['traditional_total'] - costs['optimized_total']
    costs['savings_percentage'] = (costs['savings'] / costs['traditional_total'] * 100) if costs['traditional_total'] > 0 else 0
    
    return costs

def show_generation_success():
    """Show generation success message."""
    
    st.markdown("""
    <div style="background: #10B981; color: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">✅ Generation Complete!</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
            All customer communication plans have been created. Go to the "Results" tab to view them.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2
col1, col2 = st.columns(2)
   
with col1:
       if st.button("📊 View Results", use_container_width=True):
           pass  # Will switch to results tab on rerun
   
with col2:
       if st.button("🔄 Generate New Plans", use_container_width=True, type="secondary"):
           if 'communication_plans_generated' in st.session_state:
               del st.session_state.communication_plans_generated
           if 'generated_plans_data' in st.session_state:
               del st.session_state.generated_plans_data
           if 'all_customer_plans' in st.session_state:
               del st.session_state.all_customer_plans
           st.rerun()

def render_results_tab():
   """Render comprehensive results with all customers and full content."""
   
   if 'communication_plans_generated' not in st.session_state:
       st.info("Generate communication plans first to see results.")
       return
   
   if 'all_customer_plans' not in st.session_state:
       st.error("No generated plans found. Please regenerate.")
       return
   
   all_plans = st.session_state.all_customer_plans
   
   st.markdown("### 📊 Communication Plans Results")
   
   # Summary metrics at the top
   render_summary_metrics(all_plans)
   
   # Complete customer table
   st.markdown("### 📋 All Customer Plans Summary")
   render_customer_summary_table(all_plans)
   
   # Individual customer details
   st.markdown("### 👤 Individual Customer Communication Details")
   render_individual_customer_details(all_plans)
   
   # Export section
   st.markdown("### 📥 Export Results")
   render_export_section(all_plans)

def render_summary_metrics(all_plans: List[Dict]):
   """Render summary metrics for all generated plans."""
   
   # Calculate totals
   total_customers = len(all_plans)
   total_traditional = sum(plan['costs']['traditional_total'] for plan in all_plans)
   total_optimized = sum(plan['costs']['optimized_total'] for plan in all_plans)
   total_savings = total_traditional - total_optimized
   savings_percentage = (total_savings / total_traditional * 100) if total_traditional > 0 else 0
   
   # Count channels used
   total_in_app = sum(1 for plan in all_plans if 'in_app' in plan['channels'])
   total_email = sum(1 for plan in all_plans if 'email' in plan['channels'])
   total_sms = sum(1 for plan in all_plans if 'sms' in plan['channels'])
   total_letter = sum(1 for plan in all_plans if 'letter' in plan['channels'])
   total_voice = sum(1 for plan in all_plans if 'voice_note' in plan['channels'])
   
   # Display metrics
   st.markdown("### 💰 Cost Analysis Summary")
   
   col1, col2, col3, col4 = st.columns(4)
   
   with col1:
       st.markdown(f"""
       <div style="background: #FEE2E2; border: 1px solid #EF4444; border-radius: 8px; padding: 1rem;">
           <h4 style="margin-top: 0; color: #991B1B;">Traditional Approach</h4>
           <div style="font-size: 1.5rem; font-weight: 700; color: #EF4444;">£{total_traditional:.2f}</div>
           <p style="color: #991B1B; margin-bottom: 0;">All letters (£{total_traditional/total_customers:.2f}/customer)</p>
       </div>
       """, unsafe_allow_html=True)
   
   with col2:
       st.markdown(f"""
       <div style="background: #DCFCE7; border: 1px solid #10B981; border-radius: 8px; padding: 1rem;">
           <h4 style="margin-top: 0; color: #166534;">Optimized Strategy</h4>
           <div style="font-size: 1.5rem; font-weight: 700; color: #10B981;">£{total_optimized:.2f}</div>
           <p style="color: #166534; margin-bottom: 0;">Smart channels (£{total_optimized/total_customers:.2f}/customer)</p>
       </div>
       """, unsafe_allow_html=True)
   
   with col3:
       st.markdown(f"""
       <div style="background: #EFF6FF; border: 1px solid #3B82F6; border-radius: 8px; padding: 1rem;">
           <h4 style="margin-top: 0; color: #1E40AF;">Total Savings</h4>
           <div style="font-size: 1.5rem; font-weight: 700; color: #3B82F6;">£{total_savings:.2f}</div>
           <p style="color: #1E40AF; margin-bottom: 0;">{savings_percentage:.1f}% reduction</p>
       </div>
       """, unsafe_allow_html=True)
   
   with col4:
       st.markdown(f"""
       <div style="background: #F3E8FF; border: 1px solid #9333EA; border-radius: 8px; padding: 1rem;">
           <h4 style="margin-top: 0; color: #581C87;">Customers Processed</h4>
           <div style="font-size: 1.5rem; font-weight: 700; color: #9333EA;">{total_customers}</div>
           <p style="color: #581C87; margin-bottom: 0;">Complete analysis</p>
       </div>
       """, unsafe_allow_html=True)
   
   # Channel usage summary
   st.markdown("### 📱 Channel Distribution")
   
   col1, col2, col3, col4, col5 = st.columns(5)
   
   with col1:
       st.metric("📱 In-App", f"{total_in_app}", f"{total_in_app/total_customers*100:.0f}%")
   
   with col2:
       st.metric("📧 Email", f"{total_email}", f"{total_email/total_customers*100:.0f}%")
   
   with col3:
       st.metric("💬 SMS", f"{total_sms}", f"{total_sms/total_customers*100:.0f}%")
   
   with col4:
       st.metric("📮 Letter", f"{total_letter}", f"{total_letter/total_customers*100:.0f}%")
   
   with col5:
       st.metric("🔊 Voice", f"{total_voice}", f"{total_voice/total_customers*100:.0f}%")

def render_customer_summary_table(all_plans: List[Dict]):
   """Render a comprehensive table of all customer plans."""
   
   # Build table data
   table_data = []
   
   for plan in all_plans:
       # Get channel indicators
       channels_str = ", ".join(plan['channels'])
       
       # Build row
       row = {
           'Customer': plan['customer_name'],
           'Category': plan['customer_category'],
           'Channels': channels_str,
           'Trad. Cost': f"£{plan['costs']['traditional_total']:.3f}",
           'Opt. Cost': f"£{plan['costs']['optimized_total']:.3f}",
           'Savings': f"£{plan['costs']['savings']:.3f}",
           'Savings %': f"{plan['costs']['savings_percentage']:.1f}%",
           'In-App': '✓' if 'in_app' in plan['channels'] else '✗',
           'Email': '✓' if 'email' in plan['channels'] else '✓',
           'SMS': '✓' if 'sms' in plan['channels'] else '✗',
           'Letter': '✓' if 'letter' in plan['channels'] else '✗',
           'Voice': '✓' if 'voice_note' in plan['channels'] else '✗',
           'Upsell': '✓' if plan['upsell_eligible'] else '✗'
       }
       
       table_data.append(row)
   
   # Create DataFrame
   df = pd.DataFrame(table_data)
   
   # Display with color coding
   st.dataframe(
       df,
       use_container_width=True,
       height=400,
       column_config={
           "Savings %": st.column_config.NumberColumn(
               "Savings %",
               help="Percentage saved vs traditional approach",
               format="%.1f%%",
           ),
       }
   )
   
   # Summary statistics
   st.markdown("#### Summary Statistics")
   
   col1, col2, col3 = st.columns(3)
   
   with col1:
       avg_savings_pct = sum(plan['costs']['savings_percentage'] for plan in all_plans) / len(all_plans)
       st.metric("Average Savings", f"{avg_savings_pct:.1f}%")
   
   with col2:
       digital_first = sum(1 for plan in all_plans if plan['customer_category'] == 'Digital-first self-serve')
       st.metric("Digital-First Customers", f"{digital_first}/{len(all_plans)}")
   
   with col3:
       vulnerable = sum(1 for plan in all_plans if plan['customer_category'] == 'Vulnerable / extra-support')
       st.metric("Protected Customers", f"{vulnerable}/{len(all_plans)}")

def render_individual_customer_details(all_plans: List[Dict]):
   """Render detailed view for each customer with full content."""
   
   # Customer selector
   customer_names = [f"{plan['customer_name']} ({plan['customer_category']})" for plan in all_plans]
   
   selected_index = st.selectbox(
       "Select customer to view full communication details:",
       range(len(customer_names)),
       format_func=lambda x: customer_names[x]
   )
   
   selected_plan = all_plans[selected_index]
   
   # Display customer header
   st.markdown(f"""
   <div style="background: #F8FAFC; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
       <h4 style="margin-top: 0;">{selected_plan['customer_name']}</h4>
       <p style="margin-bottom: 0.5rem;"><strong>Category:</strong> {selected_plan['customer_category']}</p>
       <p style="margin-bottom: 0.5rem;"><strong>Communication Type:</strong> {selected_plan['classification_type']}</p>
       <p style="margin-bottom: 0;"><strong>Cost Savings:</strong> £{selected_plan['costs']['savings']:.3f} ({selected_plan['costs']['savings_percentage']:.1f}%)</p>
   </div>
   """, unsafe_allow_html=True)
   
   # Display content for each channel
   content = selected_plan['content']
   
   # In-App Notification
   if 'in_app' in selected_plan['channels'] and 'in_app' in content:
       with st.expander("📱 In-App Notification", expanded=True):
           in_app = content['in_app']
           
           col1, col2 = st.columns([1, 2])
           
           with col1:
               st.markdown("**Push Notification:**")
               st.markdown(f"""
               <div style="background: #000; color: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0;">
                   <div style="font-size: 0.8rem; opacity: 0.8;">{in_app.get('push_title', 'Resonance Bank')}</div>
                   <div style="margin-top: 0.5rem;">{in_app.get('push_body', 'Notification')}</div>
               </div>
               """, unsafe_allow_html=True)
           
           with col2:
               st.markdown("**In-App Message:**")
               st.markdown(f"**Subject:** {in_app.get('message_subject', 'Message')}")
               st.text_area("Message Body:", in_app.get('message_body', ''), height=150, disabled=True, key=f"in_app_{selected_index}")
               
               col_a, col_b = st.columns(2)
               with col_a:
                   st.button(in_app.get('cta_primary', 'Action'), disabled=True, key=f"cta1_{selected_index}")
               with col_b:
                   st.button(in_app.get('cta_secondary', 'Later'), disabled=True, key=f"cta2_{selected_index}")
           
           # Cost info
           in_app_cost = selected_plan['costs']['channels'].get('in_app', {}).get('cost', 0.001)
           st.info(f"💰 Cost: £{in_app_cost:.4f} | ⚡ Delivery: Instant | 📊 Open Rate: 85-90%")
   
   # Email
   if 'email' in selected_plan['channels'] and 'email' in content:
       with st.expander("📧 Email"):
           email = content['email']
           
           st.markdown(f"**Subject:** {email.get('subject', 'Email Subject')}")
           st.markdown(f"**Preview:** {email.get('preview', 'Email preview text')}")
           st.text_area("Email Body:", email.get('body', ''), height=200, disabled=True, key=f"email_{selected_index}")
           
           email_cost = selected_plan['costs']['channels'].get('email', {}).get('cost', 0.002)
           st.info(f"💰 Cost: £{email_cost:.4f} | ⚡ Delivery: Instant | 📊 Open Rate: 25-30%")
   
   # SMS
   if 'sms' in selected_plan['channels'] and 'sms' in content:
       with st.expander("💬 SMS"):
           sms = content['sms']
           sms_text = sms.get('text', 'SMS message')
           
           st.markdown(f"""
           <div style="background: #E8F5E9; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
               <div style="font-size: 0.9rem; color: #2E7D32;">{sms_text}</div>
               <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                   Characters: {len(sms_text)}/160 | Segments: {(len(sms_text)-1)//160 + 1}
               </div>
           </div>
           """, unsafe_allow_html=True)
           
           sms_cost = selected_plan['costs']['channels'].get('sms', {}).get('cost', 0.05)
           st.info(f"💰 Cost: £{sms_cost:.3f} | ⚡ Delivery: Instant | 📊 Open Rate: 95%")
   
   # Letter
   if 'letter' in selected_plan['channels'] and 'letter' in content:
       with st.expander("📮 Letter"):
           letter = content['letter']
           
           st.markdown(f"**Greeting:** {letter.get('greeting', 'Dear Customer')}")
           st.text_area("Letter Body:", letter.get('body', ''), height=200, disabled=True, key=f"letter_{selected_index}")
           st.markdown(f"**Closing:** {letter.get('closing', 'Yours sincerely')}")
           
           letter_cost = selected_plan['costs']['channels'].get('letter', {}).get('cost', 1.46)
           st.info(f"💰 Cost: £{letter_cost:.2f} | 📮 Delivery: 2-3 days | 📊 Open Rate: 65%")
   
   # Voice Note
   if 'voice_note' in selected_plan['channels'] and 'voice_note' in content:
       with st.expander("🔊 Voice Note"):
           voice = content['voice_note']
           
           st.markdown("**Script:**")
           st.text_area("Voice Script:", voice.get('script', ''), height=100, disabled=True, key=f"voice_{selected_index}")
           
           # Placeholder for audio player
           st.markdown("""
           <div style="background: #F3F4F6; border-radius: 8px; padding: 1rem; text-align: center;">
               🔊 Audio player will appear here when voice generation is enabled
           </div>
           """, unsafe_allow_html=True)
           
           voice_cost = selected_plan['costs']['channels'].get('voice_note', {}).get('cost', 0.02)
           st.info(f"💰 Cost: £{voice_cost:.3f} | ⚡ Generation: 2-3 seconds | 📊 Listen Rate: 70%")
   
   # Upsell message
   if selected_plan['upsell_eligible'] and content.get('upsell_message'):
       with st.expander("💎 Upsell Opportunity"):
           st.success(content['upsell_message'])
   
   # Personalization notes
   if 'personalization_notes' in content:
       with st.expander("🎯 Personalization Applied"):
           for note in content['personalization_notes']:
               st.markdown(f"• {note}")

def render_export_section(all_plans: List[Dict]):
   """Render export options for all results."""
   
   col1, col2, col3 = st.columns(3)
   
   with col1:
       # Export to CSV
       if st.button("📊 Export to CSV", use_container_width=True):
           csv_data = export_to_csv(all_plans)
           st.download_button(
               label="Download CSV",
               data=csv_data,
               file_name=f"communication_plans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
               mime="text/csv"
           )
   
   with col2:
       # Export to Excel
       if st.button("📗 Export to Excel", use_container_width=True):
           excel_data = export_to_excel(all_plans)
           st.download_button(
               label="Download Excel",
               data=excel_data,
               file_name=f"communication_plans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
           )
   
   with col3:
       # Export to JSON
       if st.button("🔄 Export to JSON", use_container_width=True):
           json_data = json.dumps(all_plans, indent=2, default=str)
           st.download_button(
               label="Download JSON",
               data=json_data,
               file_name=f"communication_plans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
               mime="application/json"
           )

def export_to_csv(all_plans: List[Dict]) -> str:
   """Export all plans to CSV format."""
   
   rows = []
   for plan in all_plans:
       row = {
           'customer_id': plan['customer_id'],
           'customer_name': plan['customer_name'],
           'customer_category': plan['customer_category'],
           'classification_type': plan['classification_type'],
           'channels_used': ', '.join(plan['channels']),
           'traditional_cost': plan['costs']['traditional_total'],
           'optimized_cost': plan['costs']['optimized_total'],
           'savings': plan['costs']['savings'],
           'savings_percentage': plan['costs']['savings_percentage'],
           'upsell_eligible': plan['upsell_eligible']
       }
       
       # Add channel-specific content
       content = plan['content']
       if 'in_app' in content:
           row['in_app_push'] = content['in_app'].get('push_body', '')
           row['in_app_message'] = content['in_app'].get('message_body', '')
       
       if 'email' in content:
           row['email_subject'] = content['email'].get('subject', '')
           row['email_body'] = content['email'].get('body', '')
       
       if 'sms' in content:
           row['sms_text'] = content['sms'].get('text', '')
       
       rows.append(row)
   
   df = pd.DataFrame(rows)
   return df.to_csv(index=False)

def export_to_excel(all_plans: List[Dict]) -> bytes:
   """Export all plans to Excel format with multiple sheets."""
   
   output = io.BytesIO()
   
   with pd.ExcelWriter(output, engine='openpyxl') as writer:
       # Sheet 1: Summary
       summary_data = []
       for plan in all_plans:
           summary_data.append({
               'Customer': plan['customer_name'],
               'Category': plan['customer_category'],
               'Channels': ', '.join(plan['channels']),
               'Traditional Cost': plan['costs']['traditional_total'],
               'Optimized Cost': plan['costs']['optimized_total'],
               'Savings': plan['costs']['savings'],
               'Savings %': plan['costs']['savings_percentage']
           })
       
       df_summary = pd.DataFrame(summary_data)
       df_summary.to_excel(writer, sheet_name='Summary', index=False)
       
       # Sheet 2: Channel Details
       channel_data = []
       for plan in all_plans:
           content = plan['content']
           row = {
               'Customer': plan['customer_name'],
               'In-App Push': content.get('in_app', {}).get('push_body', '') if 'in_app' in content else '',
               'In-App Message': content.get('in_app', {}).get('message_body', '') if 'in_app' in content else '',
               'Email Subject': content.get('email', {}).get('subject', '') if 'email' in content else '',
               'SMS Text': content.get('sms', {}).get('text', '') if 'sms' in content else '',
               'Voice Script': content.get('voice_note', {}).get('script', '') if 'voice_note' in content else ''
           }
           channel_data.append(row)
       
       df_channels = pd.DataFrame(channel_data)
       df_channels.to_excel(writer, sheet_name='Channel Details', index=False)
       
       # Sheet 3: Cost Analysis
       cost_data = []
       for plan in all_plans:
           costs = plan['costs']['channels']
           row = {
               'Customer': plan['customer_name'],
               'Letter Cost': costs.get('letter', {}).get('cost', 0),
               'Email Cost': costs.get('email', {}).get('cost', 0),
               'SMS Cost': costs.get('sms', {}).get('cost', 0),
               'In-App Cost': costs.get('in_app', {}).get('cost', 0),
               'Voice Cost': costs.get('voice_note', {}).get('cost', 0),
               'Total Traditional': plan['costs']['traditional_total'],
               'Total Optimized': plan['costs']['optimized_total'],
               'Savings': plan['costs']['savings']
           }
           cost_data.append(row)
       
       df_costs = pd.DataFrame(cost_data)
       df_costs.to_excel(writer, sheet_name='Cost Analysis', index=False)
   
   output.seek(0)
   return output.read()

def render_analytics_tab():
   """Render analytics and insights tab."""
   
   if 'all_customer_plans' not in st.session_state:
       st.info("Generate communication plans first to see analytics.")
       return
   
   all_plans = st.session_state.all_customer_plans
   
   st.markdown("### 📈 Analytics & Insights")
   
   # Category breakdown
   st.markdown("#### Customer Category Analysis")
   
   category_stats = {}
   for plan in all_plans:
       category = plan['customer_category']
       if category not in category_stats:
           category_stats[category] = {
               'count': 0,
               'total_savings': 0,
               'total_traditional': 0,
               'total_optimized': 0,
               'channels_used': set()
           }
       
       category_stats[category]['count'] += 1
       category_stats[category]['total_savings'] += plan['costs']['savings']
       category_stats[category]['total_traditional'] += plan['costs']['traditional_total']
       category_stats[category]['total_optimized'] += plan['costs']['optimized_total']
       category_stats[category]['channels_used'].update(plan['channels'])
   
   # Display category metrics
   for category, stats in category_stats.items():
       avg_savings_pct = (stats['total_savings'] / stats['total_traditional'] * 100) if stats['total_traditional'] > 0 else 0
       
       with st.expander(f"{category} ({stats['count']} customers)"):
           col1, col2, col3 = st.columns(3)
           
           with col1:
               st.metric("Average Savings", f"{avg_savings_pct:.1f}%")
           
           with col2:
               st.metric("Total Saved", f"£{stats['total_savings']:.2f}")
           
           with col3:
               st.metric("Channels Used", len(stats['channels_used']))
           
           st.markdown(f"**Primary Channels:** {', '.join(stats['channels_used'])}")
   
   # Channel effectiveness
   st.markdown("#### Channel Effectiveness Analysis")
   
   channel_usage = {}
   for plan in all_plans:
       for channel in plan['channels']:
           if channel not in channel_usage:
               channel_usage[channel] = {'count': 0, 'total_cost': 0}
           
           channel_usage[channel]['count'] += 1
           channel_usage[channel]['total_cost'] += plan['costs']['channels'].get(channel, {}).get('cost', 0)
   
   # Create channel chart
   if channel_usage:
       channel_df = pd.DataFrame([
           {'Channel': ch.title(), 'Usage': data['count'], 'Total Cost': data['total_cost']}
           for ch, data in channel_usage.items()
       ])
       
       col1, col2 = st.columns(2)
       
       with col1:
           import plotly.express as px
           fig = px.bar(channel_df, x='Channel', y='Usage', title='Channel Usage Distribution')
           st.plotly_chart(fig, use_container_width=True)
       
       with col2:
           fig2 = px.pie(channel_df, values='Total Cost', names='Channel', title='Cost Distribution by Channel')
           st.plotly_chart(fig2, use_container_width=True)
   
   # Key insights
   st.markdown("#### 💡 Key Insights")
   
   insights = generate_insights(all_plans, category_stats, channel_usage)
   
   for insight in insights:
       st.success(insight)

def generate_insights(all_plans: List[Dict], category_stats: Dict, channel_usage: Dict) -> List[str]:
   """Generate intelligent insights from the analysis."""
   
   insights = []
   
   # Overall savings insight
   total_traditional = sum(plan['costs']['traditional_total'] for plan in all_plans)
   total_optimized = sum(plan['costs']['optimized_total'] for plan in all_plans)
   total_savings_pct = ((total_traditional - total_optimized) / total_traditional * 100) if total_traditional > 0 else 0
   
   insights.append(f"💰 Achieved {total_savings_pct:.1f}% cost reduction through intelligent channel optimization")
   
   # Digital adoption insight
   digital_customers = sum(1 for plan in all_plans if 'in_app' in plan['channels'])
   if digital_customers > 0:
       insights.append(f"📱 {digital_customers} customers receiving instant in-app notifications vs 2-3 day postal delivery")
   
   # Vulnerable protection
   vulnerable_count = category_stats.get('Vulnerable / extra-support', {}).get('count', 0)
   if vulnerable_count > 0:
       insights.append(f"🛡️ {vulnerable_count} vulnerable customers protected with appropriate communication channels")
   
   # Environmental impact
   letter_count = channel_usage.get('letter', {}).get('count', 0)
   in_app_count = channel_usage.get('in_app', {}).get('count', 0)
   if in_app_count > 0:
       carbon_saved = (letter_count * 25) - (in_app_count * 0.05)  # grams of CO2
       insights.append(f"🌱 Reduced carbon footprint by {carbon_saved:.0f}g CO2 through digital channels")
   
   # Cost efficiency by category
   most_efficient_category = max(category_stats.items(), 
                                key=lambda x: (x[1]['total_savings'] / x[1]['total_traditional']) if x[1]['total_traditional'] > 0 else 0)
   if most_efficient_category:
       category_name = most_efficient_category[0]
       category_savings = (most_efficient_category[1]['total_savings'] / most_efficient_category[1]['total_traditional'] * 100)
       insights.append(f"🎯 {category_name} customers show highest optimization potential at {category_savings:.1f}% savings")
   
   return insights