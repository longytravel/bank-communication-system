"""
Channel Display Components
Handles the display of individual communication channels in the UI.
FIXED: Spanish language detection and voice generation.
"""

import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional
import sys
sys.path.append('src')


def detect_language_from_text(text: str) -> str:
    """
    Detect language from text content.
    Returns 'Spanish' if Spanish indicators found, otherwise 'English'.
    """
    if not text:
        return 'English'
    
    # Spanish indicator words
    spanish_indicators = [
        'hola', 'gracias', 'señor', 'señora', 'cuenta', 
        'banco', 'usted', 'está', 'día', 'queremos',
        'servicios', 'acceso', 'conocer', 'más', 'para',
        'con', 'por', 'como', 'cuando', 'donde', 'porque',
        'también', 'después', 'ahora', 'nuevo', 'nuestro'
    ]
    
    text_lower = text.lower()
    spanish_word_count = sum(1 for word in spanish_indicators if word in text_lower)
    
    # If we find 3+ Spanish words, it's likely Spanish
    return 'Spanish' if spanish_word_count >= 3 else 'English'


def render_video_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the video message channel display."""
    if 'video_message' not in content:
        return
        
    with st.expander("🎬 Personalized Video Message", expanded=True):
        video_content = content['video_message']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Video Script:**")
            video_script = video_content.get('script', '')
            st.text_area("Script:", video_script, height=150, disabled=True, 
                        key=f"video_script_{selected_index}")
            
            st.markdown(f"**Greeting:** {video_content.get('greeting', 'Hello')}")
            st.markdown(f"**Closing:** {video_content.get('closing', 'Thank you')}")
        
        with col2:
            st.markdown("**Video Details:**")
            st.markdown(f"- **Tier:** {video_content.get('tier', 'SILVER')}")
            st.markdown(f"- **Duration:** {video_content.get('duration', '15-20 seconds')}")
            st.markdown(f"- **Avatar:** {video_content.get('avatar', 'Professional banker')}")
            
            # Check for existing video
            customer_id = selected_plan.get('customer_id', 'unknown')
            video_dir = Path("data/video_messages")
            video_file = None
            
            if video_dir.exists():
                # Look for existing video file
                video_files = list(video_dir.glob(f"{customer_id}*.mp4"))
                if video_files:
                    video_file = video_files[0]  # Get most recent
            
            if video_file and video_file.exists():
                st.success("✅ Video generated")
                with open(video_file, 'rb') as vf:
                    st.video(vf.read())
            else:
                if st.button("🎬 Generate Video Now", key=f"gen_video_{selected_index}"):
                    with st.spinner("Generating personalized video..."):
                        try:
                            from api.api_manager import APIManager
                            api_manager = APIManager()
                            
                            # Detect language from script
                            detected_language = detect_language_from_text(video_script)
                            customer_language = selected_plan.get('customer_language', detected_language)
                            
                            # Generate video with customer data for language selection
                            video_path = api_manager.generate_video_message(
                                video_script,
                                customer_id,
                                "personalized",
                                customer_data={
                                    'preferred_language': customer_language,
                                    'name': selected_plan.get('customer_name', ''),
                                    'account_balance': selected_plan.get('account_balance', 0)
                                }
                            )
                            
                            if video_path and video_path.exists():
                                st.success("✅ Video generated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to generate video")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        # Cost information
        video_cost = selected_plan['costs']['channels'].get('video_message', {}).get('cost', 0.50)
        tier = video_content.get('tier', 'high-value')
        st.info(f"💰 Cost: £{video_cost:.2f} | ⚡ Generation: 10-15 seconds | "
                f"🎯 Premium experience for {tier} customers")


def render_inapp_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the in-app notification channel display."""
    if 'in_app' not in content:
        return
        
    with st.expander("📱 In-App Notification", expanded=False):
        in_app_content = content['in_app']
        
        if isinstance(in_app_content, dict):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Push Notification:**")
                push_title = in_app_content.get('push_title', 'Resonance Bank')
                push_body = in_app_content.get('push_body', '')
                st.info(f"**{push_title}**\n\n{push_body}")
                
                st.markdown("**In-App Message:**")
                st.text_area("Subject:", 
                           in_app_content.get('message_subject', ''), 
                           height=50, disabled=True, 
                           key=f"inapp_subject_{selected_index}")
                st.text_area("Message:", 
                           in_app_content.get('message_body', ''), 
                           height=100, disabled=True, 
                           key=f"inapp_body_{selected_index}")
            
            with col2:
                st.markdown("**Action Buttons:**")
                st.button(in_app_content.get('cta_primary', 'Review Now'), 
                         key=f"cta1_{selected_index}", disabled=True)
                st.button(in_app_content.get('cta_secondary', 'Later'), 
                         key=f"cta2_{selected_index}", disabled=True)
        else:
            # Simple text display
            st.text_area("Notification:", str(in_app_content), height=100, 
                        disabled=True, key=f"inapp_text_{selected_index}")
        
        # Cost information
        in_app_cost = selected_plan['costs']['channels'].get('in_app', {}).get('cost', 0.001)
        st.success(f"💰 Cost: £{in_app_cost:.4f} | ⚡ Instant delivery | "
                   f"📱 Native app experience")


def render_email_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the email channel display."""
    if 'email' not in content:
        return
        
    with st.expander("📧 Email Communication", expanded=False):
        email_content = content['email']
        
        if isinstance(email_content, dict):
            st.markdown("**Email Details:**")
            st.text_input("Subject Line:", 
                         email_content.get('subject', ''), 
                         disabled=True, 
                         key=f"email_subject_{selected_index}")
            st.text_input("Preview Text:", 
                         email_content.get('preview', ''), 
                         disabled=True, 
                         key=f"email_preview_{selected_index}")
            
            st.markdown("**Email Body:**")
            email_body = email_content.get('body', '')
            st.text_area("Content:", email_body, height=200, 
                        disabled=True, key=f"email_body_{selected_index}")
            
            # HTML preview if available
            if 'html' in email_content:
                with st.expander("View HTML Preview"):
                    st.markdown(email_content['html'], unsafe_allow_html=True)
        else:
            # Simple text display
            st.text_area("Email Content:", str(email_content), height=150, 
                        disabled=True, key=f"email_text_{selected_index}")
        
        # Cost information
        email_cost = selected_plan['costs']['channels'].get('email', {}).get('cost', 0.002)
        st.info(f"💰 Cost: £{email_cost:.4f} | 📊 Trackable | "
                f"✉️ Durable medium for regulatory")


def render_sms_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the SMS channel display."""
    if 'sms' not in content:
        return
        
    with st.expander("💬 SMS Message", expanded=False):
        sms_content = content.get('sms', {})
        
        # Extract SMS text
        if isinstance(sms_content, dict):
            sms_text = sms_content.get('text', '')
        else:
            sms_text = str(sms_content)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_area("SMS Text:", sms_text, height=100, 
                        disabled=True, key=f"sms_text_{selected_index}")
        
        with col2:
            # SMS metrics
            char_count = len(sms_text)
            messages_needed = (char_count + 159) // 160  # Ceiling division
            
            st.markdown("**SMS Details:**")
            st.metric("Characters", f"{char_count}/160")
            st.metric("Messages", messages_needed)
            
            # Status indicator
            if char_count <= 160:
                st.success("✅ Single SMS")
            elif char_count <= 320:
                st.warning("⚠️ 2 SMS parts")
            else:
                st.error("❌ Consider shortening")
        
        # Cost calculation
        sms_cost = selected_plan['costs']['channels'].get('sms', {}).get('cost', 0.05)
        total_sms_cost = sms_cost * messages_needed
        st.info(f"💰 Cost: £{total_sms_cost:.3f} | ⚡ 98% open rate | "
                f"📱 Direct to mobile")


def render_voice_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """
    Render the voice note channel display.
    FIXED: Properly detects and uses Spanish language.
    """
    if 'voice_note' not in content:
        return
        
    with st.expander("🔊 Voice Note", expanded=False):
        voice_content = content.get('voice_note', {})
        
        # Extract the script text
        if isinstance(voice_content, dict):
            voice_script = voice_content.get('script', '')
        else:
            voice_script = str(voice_content)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Voice Script:**")
            st.text_area("Script:", voice_script, height=150, 
                        disabled=True, key=f"voice_script_{selected_index}")
        
        with col2:
            st.markdown("**Audio Details:**")
            
            # Calculate duration estimate
            word_count = len(voice_script.split()) if voice_script else 0
            estimated_duration = (word_count / 150) * 60  # 150 words per minute
            st.metric("Duration", f"~{estimated_duration:.0f} seconds")
            
            # Check for existing audio file
            customer_id = selected_plan.get('customer_id', 'unknown')
            voice_dir = Path("data/voice_notes")
            voice_file = None
            
            if voice_dir.exists():
                # Look for most recent voice file for this customer
                voice_files = list(voice_dir.glob(f"{customer_id}*.mp3"))
                if voice_files:
                    # Sort by modification time and get the most recent
                    voice_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    voice_file = voice_files[0]
            
            if voice_file and voice_file.exists():
                st.success("✅ Audio generated")
                with open(voice_file, 'rb') as audio_file:
                    st.audio(audio_file.read(), format='audio/mp3')
            else:
                if st.button("🔊 Generate Audio", key=f"gen_voice_{selected_index}"):
                    with st.spinner("Generating voice note..."):
                        generate_voice_note(voice_script, customer_id, selected_plan)
        
        # Cost information
        voice_cost = selected_plan['costs']['channels'].get('voice_note', {}).get('cost', 0.02)
        st.info(f"💰 Cost: £{voice_cost:.3f} | 🎧 Accessible format | "
                f"📱 Listen on-the-go")


def generate_voice_note(voice_script: str, customer_id: str, selected_plan: Dict):
    """
    Generate voice note with proper language detection.
    Separated function for cleaner code.
    """
    try:
        from api.api_manager import APIManager
        api_manager = APIManager()
        
        # CRITICAL: Detect language from the actual text
        detected_language = detect_language_from_text(voice_script)
        
        # Check if customer has explicit language preference
        customer_language = selected_plan.get('customer_language', None)
        
        # If no explicit language, check customer name for hints
        if not customer_language:
            customer_name = selected_plan.get('customer_name', '')
            spanish_surnames = ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 
                               'Gonzalez', 'Sanchez', 'Ramirez', 'Torres']
            if any(surname in customer_name for surname in spanish_surnames):
                customer_language = 'Spanish'
        
        # Use detected language if no customer preference
        final_language = customer_language or detected_language
        
        # Debug output for troubleshooting
        print("=" * 60)
        print("VOICE GENERATION DEBUG:")
        print(f"  Customer ID: {customer_id}")
        print(f"  Customer Name: {selected_plan.get('customer_name', 'Unknown')}")
        print(f"  Language in plan: {selected_plan.get('customer_language', 'NOT SET')}")
        print(f"  Detected from text: {detected_language}")
        print(f"  Final language: {final_language}")
        print(f"  Script preview: {voice_script[:100]}...")
        print("=" * 60)
        
        # Generate voice note with proper language
        voice_path = api_manager.openai.generate_voice_note(
            voice_script,
            customer_id,
            "notification",
            customer_language=final_language
        )
        
        if voice_path and voice_path.exists():
            st.success(f"✅ Voice note generated in {final_language}!")
            st.rerun()
        else:
            st.error("Failed to generate voice note")
            
    except Exception as e:
        print(f"ERROR in voice generation: {e}")
        import traceback
        traceback.print_exc()
        st.error(f"Error: {str(e)}")


def render_letter_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the postal letter channel display."""
    if 'letter' not in content:
        return
        
    with st.expander("📮 Postal Letter", expanded=False):
        letter_content = content.get('letter', {})
        
        if isinstance(letter_content, dict):
            st.markdown("**Letter Components:**")
            
            st.text_input("Greeting:", 
                         letter_content.get('greeting', 'Dear Customer'), 
                         disabled=True, 
                         key=f"letter_greeting_{selected_index}")
            
            st.text_area("Letter Body:", 
                        letter_content.get('body', ''), 
                        height=200, 
                        disabled=True, 
                        key=f"letter_body_{selected_index}")
            
            st.text_input("Closing:", 
                         letter_content.get('closing', 'Yours sincerely'), 
                         disabled=True, 
                         key=f"letter_closing_{selected_index}")
        else:
            # Simple text display
            st.text_area("Letter Content:", str(letter_content), height=200, 
                        disabled=True, key=f"letter_text_{selected_index}")
        
        # Cost information with breakdown
        letter_cost = selected_plan['costs']['channels'].get('letter', {}).get('cost', 1.46)
        st.warning(f"💰 Cost: £{letter_cost:.2f} | 📬 2-3 day delivery | "
                   f"✅ Durable medium compliant")
        
        with st.expander("Cost Breakdown"):
            st.markdown("""
            - Postage: £0.85
            - Printing: £0.08
            - Envelope: £0.03
            - Processing: £0.50
            """)


def render_upsell_section(content: Dict, selected_plan: Dict):
    """Render the upsell opportunity section if applicable."""
    if not selected_plan.get('upsell_eligible'):
        return
        
    upsell_message = content.get('upsell_message')
    if not upsell_message:
        return
        
    with st.expander("💎 Upsell Opportunity", expanded=False):
        st.info(upsell_message)
        
        # Classification-specific warnings
        classification = selected_plan.get('classification_type', '')
        if classification == 'REGULATORY':
            st.warning("⚠️ Note: Upsell content excluded from regulatory communication")
        else:
            st.success("✅ Upsell message included in appropriate channels")


def render_personalization_notes(content: Dict):
    """Render the personalization notes section."""
    notes = content.get('personalization_notes', [])
    if not notes:
        return
        
    with st.expander("📝 Personalization Applied", expanded=False):
        st.markdown("**AI Personalization Points:**")
        for note in notes:
            st.markdown(f"• {note}")


def render_all_channels(selected_plan: Dict, selected_index: int):
    """
    Main function to render all communication channels for a customer.
    This is called from the main UI to display all channels.
    
    Args:
        selected_plan: Customer's communication plan data
        selected_index: Index for unique widget keys
    """
    content = selected_plan.get('content', {})
    channels = selected_plan.get('channels', [])
    
    # Display channels in priority order
    
    # 1. Video (premium channel)
    if 'video_message' in channels:
        render_video_channel(content, selected_plan, selected_index)
    
    # 2. Digital channels
    if 'in_app' in channels:
        render_inapp_channel(content, selected_plan, selected_index)
    
    if 'email' in channels:
        render_email_channel(content, selected_plan, selected_index)
    
    if 'sms' in channels:
        render_sms_channel(content, selected_plan, selected_index)
    
    if 'voice_note' in channels:
        render_voice_channel(content, selected_plan, selected_index)
    
    # 3. Traditional channels
    if 'letter' in channels:
        render_letter_channel(content, selected_plan, selected_index)
    
    # 4. Additional sections
    render_upsell_section(content, selected_plan)
    render_personalization_notes(content)