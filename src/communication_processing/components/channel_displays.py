"""
Channel Display Components
Handles the display of individual communication channels in the UI.
This is extracted from customer_plans_ui.py to make it more manageable.
"""

import streamlit as st
from pathlib import Path
from typing import Dict, Any

def render_video_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the video message channel display."""
    if 'video_message' not in content:
        return
        
    with st.expander("🎬 Personalized Video Message", expanded=True):
        video_content = content['video_message']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Video Script:**")
            st.text_area("Script:", video_content.get('script', ''), height=150, disabled=True, key=f"video_script_{selected_index}")
            
            st.markdown(f"**Greeting:** {video_content.get('greeting', 'Hello')}")
            st.markdown(f"**Closing:** {video_content.get('closing', 'Thank you')}")
        
        with col2:
            st.markdown("**Video Details:**")
            st.markdown(f"- **Tier:** {video_content.get('tier', 'SILVER')}")
            st.markdown(f"- **Duration:** {video_content.get('duration', '15-20 seconds')}")
            st.markdown(f"- **Avatar:** {video_content.get('avatar', 'Professional banker')}")
            
            # Generate video button
            customer_id = selected_plan.get('customer_id', 'unknown')
            video_dir = Path("data/video_messages")
            video_file = None
            
            if video_dir.exists():
                for file in video_dir.glob(f"{customer_id}*.mp4"):
                    video_file = file
                    break
            
            if video_file and video_file.exists():
                st.success("✅ Video generated")
                with open(video_file, 'rb') as vf:
                    video_bytes = vf.read()
                    st.video(video_bytes)
            else:
                if st.button("🎬 Generate Video Now", key=f"gen_video_{selected_index}"):
                    with st.spinner("Generating personalized video..."):
                        try:
                            from api.api_manager import APIManager
                            api_manager = APIManager()
                            
                            video_path = api_manager.generate_video_message(
                                video_content.get('script', ''),
                                customer_id,
                                "personalized"
                            )
                            
                            if video_path and video_path.exists():
                                st.success("✅ Video generated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to generate video")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        video_cost = selected_plan['costs']['channels'].get('video_message', {}).get('cost', 0.50)
        st.info(f"💰 Cost: £{video_cost:.2f} | ⚡ Generation: 10-15 seconds | 🎯 Premium experience for {video_content.get('tier', 'high-value')} customers")


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
                st.info(f"**{in_app_content.get('push_title', 'Resonance Bank')}**\n\n{in_app_content.get('push_body', '')}")
                
                st.markdown("**In-App Message:**")
                st.text_area(
                    "Subject:", 
                    in_app_content.get('message_subject', ''), 
                    height=50, 
                    disabled=True, 
                    key=f"inapp_subject_{selected_index}"
                )
                st.text_area(
                    "Message:", 
                    in_app_content.get('message_body', ''), 
                    height=100, 
                    disabled=True, 
                    key=f"inapp_body_{selected_index}"
                )
            
            with col2:
                st.markdown("**Action Buttons:**")
                st.button(in_app_content.get('cta_primary', 'Review Now'), key=f"cta1_{selected_index}", disabled=True)
                st.button(in_app_content.get('cta_secondary', 'Later'), key=f"cta2_{selected_index}", disabled=True)
        else:
            st.text_area("Notification:", str(in_app_content), height=100, disabled=True, key=f"inapp_text_{selected_index}")
        
        in_app_cost = selected_plan['costs']['channels'].get('in_app', {}).get('cost', 0.001)
        st.success(f"💰 Cost: £{in_app_cost:.4f} | ⚡ Instant delivery | 📱 Native app experience")


def render_email_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the email channel display."""
    if 'email' not in content:
        return
        
    with st.expander("📧 Email Communication", expanded=False):
        email_content = content['email']
        
        if isinstance(email_content, dict):
            st.markdown("**Email Details:**")
            st.text_input(
                "Subject Line:", 
                email_content.get('subject', ''), 
                disabled=True, 
                key=f"email_subject_{selected_index}"
            )
            st.text_input(
                "Preview Text:", 
                email_content.get('preview', ''), 
                disabled=True, 
                key=f"email_preview_{selected_index}"
            )
            
            st.markdown("**Email Body:**")
            email_body = email_content.get('body', '')
            st.text_area(
                "Content:", 
                email_body, 
                height=200, 
                disabled=True, 
                key=f"email_body_{selected_index}"
            )
            
            if 'html' in email_content:
                with st.expander("View HTML Preview"):
                    st.markdown(email_content['html'], unsafe_allow_html=True)
        else:
            st.text_area("Email Content:", str(email_content), height=150, disabled=True, key=f"email_text_{selected_index}")
        
        email_cost = selected_plan['costs']['channels'].get('email', {}).get('cost', 0.002)
        st.info(f"💰 Cost: £{email_cost:.4f} | 📊 Trackable | ✉️ Durable medium for regulatory")


def render_sms_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the SMS channel display."""
    if 'sms' not in content:
        return
        
    with st.expander("💬 SMS Message", expanded=False):
        sms_content = content.get('sms', {})
        
        if isinstance(sms_content, dict):
            sms_text = sms_content.get('text', '')
        else:
            sms_text = str(sms_content)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_area(
                "SMS Text:", 
                sms_text, 
                height=100, 
                disabled=True, 
                key=f"sms_text_{selected_index}"
            )
        
        with col2:
            char_count = len(sms_text)
            messages_needed = (char_count // 160) + (1 if char_count % 160 else 0)
            
            st.markdown("**SMS Details:**")
            st.metric("Characters", f"{char_count}/160")
            st.metric("Messages", messages_needed)
            
            if char_count <= 160:
                st.success("✅ Single SMS")
            elif char_count <= 320:
                st.warning("⚠️ 2 SMS parts")
            else:
                st.error("❌ Consider shortening")
        
        sms_cost = selected_plan['costs']['channels'].get('sms', {}).get('cost', 0.05)
        total_sms_cost = sms_cost * messages_needed
        st.info(f"💰 Cost: £{total_sms_cost:.3f} | ⚡ 98% open rate | 📱 Direct to mobile")


def render_voice_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the voice note channel display."""
    if 'voice_note' not in content:
        return
        
    with st.expander("🔊 Voice Note", expanded=False):
        voice_content = content.get('voice_note', {})
        
        if isinstance(voice_content, dict):
            voice_script = voice_content.get('script', '')
        else:
            voice_script = str(voice_content)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Voice Script:**")
            st.text_area(
                "Script:", 
                voice_script, 
                height=150, 
                disabled=True, 
                key=f"voice_script_{selected_index}"
            )
        
        with col2:
            st.markdown("**Audio Details:**")
            word_count = len(voice_script.split())
            estimated_duration = word_count / 150 * 60
            st.metric("Duration", f"~{estimated_duration:.0f} seconds")
            
            customer_id = selected_plan.get('customer_id', 'unknown')
            voice_dir = Path("data/voice_notes")
            voice_file = None
            
            if voice_dir.exists():
                for file in voice_dir.glob(f"{customer_id}*.mp3"):
                    voice_file = file
                    break
            
            if voice_file and voice_file.exists():
                st.success("✅ Audio generated")
                with open(voice_file, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format='audio/mp3')
            else:
                if st.button("🔊 Generate Audio", key=f"gen_voice_{selected_index}"):
                    with st.spinner("Generating voice note..."):
                        try:
                            from api.api_manager import APIManager
                            api_manager = APIManager()
                            
                            voice_path = api_manager.openai.generate_voice_note(
                                voice_script,
                                customer_id,
                                "notification"
                            )
                            
                            if voice_path and voice_path.exists():
                                st.success("✅ Voice note generated!")
                                st.rerun()
                            else:
                                st.error("Failed to generate voice note")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        voice_cost = selected_plan['costs']['channels'].get('voice_note', {}).get('cost', 0.02)
        st.info(f"💰 Cost: £{voice_cost:.3f} | 🎧 Accessible format | 📱 Listen on-the-go")


def render_letter_channel(content: Dict, selected_plan: Dict, selected_index: int):
    """Render the postal letter channel display."""
    if 'letter' not in content:
        return
        
    with st.expander("📮 Postal Letter", expanded=False):
        letter_content = content.get('letter', {})
        
        if isinstance(letter_content, dict):
            st.markdown("**Letter Components:**")
            
            st.text_input(
                "Greeting:", 
                letter_content.get('greeting', 'Dear Customer'), 
                disabled=True, 
                key=f"letter_greeting_{selected_index}"
            )
            
            st.text_area(
                "Letter Body:", 
                letter_content.get('body', ''), 
                height=200, 
                disabled=True, 
                key=f"letter_body_{selected_index}"
            )
            
            st.text_input(
                "Closing:", 
                letter_content.get('closing', 'Yours sincerely'), 
                disabled=True, 
                key=f"letter_closing_{selected_index}"
            )
        else:
            st.text_area("Letter Content:", str(letter_content), height=200, disabled=True, key=f"letter_text_{selected_index}")
        
        letter_cost = selected_plan['costs']['channels'].get('letter', {}).get('cost', 1.46)
        st.warning(f"💰 Cost: £{letter_cost:.2f} | 📬 2-3 day delivery | ✅ Durable medium compliant")
        
        with st.expander("Cost Breakdown"):
            st.markdown("""
            - Postage: £0.85
            - Printing: £0.08
            - Envelope: £0.03
            - Processing: £0.50
            """)


def render_upsell_section(content: Dict, selected_plan: Dict):
    """Render the upsell opportunity section if applicable."""
    if selected_plan.get('upsell_eligible') and content.get('upsell_message'):
        with st.expander("💎 Upsell Opportunity", expanded=False):
            st.info(content['upsell_message'])
            
            if selected_plan.get('classification_type') == 'REGULATORY':
                st.warning("⚠️ Note: Upsell content excluded from regulatory communication")
            else:
                st.success("✅ Upsell message included in appropriate channels")


def render_personalization_notes(content: Dict):
    """Render the personalization notes section."""
    if content.get('personalization_notes'):
        with st.expander("📝 Personalization Applied", expanded=False):
            st.markdown("**AI Personalization Points:**")
            for note in content['personalization_notes']:
                st.markdown(f"• {note}")


def render_all_channels(selected_plan: Dict, selected_index: int):
    """
    Main function to render all communication channels for a customer.
    This is called from the main UI to display all channels.
    """
    content = selected_plan.get('content', {})
    
    # Display channels in order of importance
    # Video first (if eligible)
    if 'video_message' in selected_plan['channels']:
        render_video_channel(content, selected_plan, selected_index)
    
    # Then digital channels
    if 'in_app' in selected_plan['channels']:
        render_inapp_channel(content, selected_plan, selected_index)
    
    if 'email' in selected_plan['channels']:
        render_email_channel(content, selected_plan, selected_index)
    
    if 'sms' in selected_plan['channels']:
        render_sms_channel(content, selected_plan, selected_index)
    
    if 'voice_note' in selected_plan['channels']:
        render_voice_channel(content, selected_plan, selected_index)
    
    # Finally traditional channels
    if 'letter' in selected_plan['channels']:
        render_letter_channel(content, selected_plan, selected_index)
    
    # Additional sections
    render_upsell_section(content, selected_plan)
    render_personalization_notes(content)