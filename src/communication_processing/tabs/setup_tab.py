"""
Setup Tab Module
Handles the setup and configuration for communication planning.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from business_rules.video_rules import VideoEligibilityRules

def render_setup_tab():
    """Render the setup tab for communication planning."""
    
    st.markdown("### 👥 Customer Portfolio Summary")
    
    # Get customer data from session state
    customer_categories = st.session_state.analysis_results.get('customer_categories', [])
    aggregates = st.session_state.analysis_results.get('aggregates', {})
    
    # Calculate video eligible customers
    video_rules = VideoEligibilityRules()
    video_stats = video_rules.get_video_statistics(customer_categories)
       
    # Display customer metrics with video stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
    
    with col5:
        # NEW: Video eligible metric
        video_eligible = video_stats.get('video_eligible', 0)
        st.metric("🎬 Video Eligible", f"{video_eligible:,}")      
    
    # Video eligibility breakdown
    if video_eligible > 0:
        st.markdown("### 🎬 Video Eligibility Analysis")
        vcol1, vcol2, vcol3, vcol4 = st.columns(4)
        
        with vcol1:
            st.metric("Platinum Tier", f"{video_stats.get('platinum_tier', 0)}", "£50k+ balance")
        
        with vcol2:
            st.metric("Gold Tier", f"{video_stats.get('gold_tier', 0)}", "£25k+ balance")
        
        with vcol3:
            st.metric("Silver Tier", f"{video_stats.get('silver_tier', 0)}", "£10k+ balance")
        
        with vcol4:
            eligibility_rate = video_stats.get('eligibility_rate', 0)
            st.metric("Eligibility Rate", f"{eligibility_rate:.1f}%", f"Avg score: {video_stats.get('average_score', 0):.0f}/100")
    
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
            
            col1, col2, col3, col4 = st.columns(4)
            
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
                generate_videos = st.checkbox(
                    "🎬 Generate videos",
                    value=True,
                    help="Create personalized videos for high-value digital customers (£10k+)"
                )
            
            with col4:
                customer_filter = st.selectbox(
                    "Customer Selection",
                    ["First 20", "First 10", "First 5", "Digital-first only", "High-value only", "Video-eligible only"],
                    help="Choose which customers to process (max 20)"
                )
            
            # Store processing options
            st.session_state.processing_options = {
                'personalization_level': personalization_level,
                'generate_voice_notes': generate_voice_notes,
                'generate_videos': generate_videos,
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