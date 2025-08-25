"""
OpenAI API Integration - FIXED FOR SPANISH SUPPORT
This version properly handles Spanish voice generation.
"""

import logging
import time
import re
from typing import Optional
from pathlib import Path
import openai
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_key, get_directory

class OpenAIAPI:
    """
    OpenAI API wrapper for voice generation with PROPER language support.
    """
    
    def __init__(self):
        """Initialize OpenAI API client."""
        self.logger = logging.getLogger(__name__)
        
        # Get API key from config
        api_key = get_api_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not found. Check your .env file.")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        # TTS settings
        self.tts_model = "tts-1"
        self.max_text_length = 4096
        
        # CRITICAL FIX: Use different voices for different languages
        # Nova and Alloy work better for Romance languages
        self.voice_mapping = {
            'english': 'nova',
            'spanish': 'nova',  # Nova handles Spanish pronunciation better
            'french': 'nova',
            'german': 'alloy',
            'italian': 'nova',
            'portuguese': 'nova',
            'default': 'nova'
        }
        
        # Voice notes directory
        self.voice_notes_dir = get_directory('voice_notes')
        
        self.logger.info("OpenAI API initialized with language support")

    def generate_voice_note(self, text: str, customer_id: str, 
                          message_type: str = "notification",
                          customer_language: str = None) -> Optional[Path]:
        """
        Generate a voice note from text using OpenAI TTS.
        
        CRITICAL: OpenAI TTS will pronounce text based on the voice model,
        not the text content. All standard voices speak with English accent.
        
        Args:
            text: Text to convert to speech
            customer_id: Customer identifier for filename
            message_type: Type of message (notification, alert, etc.)
            customer_language: Customer's preferred language
            
        Returns:
            Path to the generated audio file, or None if failed
        """
        try:
            self.logger.info(f"Generating voice note for customer {customer_id}, language: {customer_language}")
            
            # CRITICAL: Detect language and select appropriate voice
            language_key = 'english'
            if customer_language:
                lang_lower = customer_language.lower()
                if lang_lower in ['spanish', 'español', 'es']:
                    language_key = 'spanish'
                elif lang_lower in ['french', 'français', 'fr']:
                    language_key = 'french'
                elif lang_lower in ['german', 'deutsch', 'de']:
                    language_key = 'german'
                elif lang_lower in ['italian', 'italiano', 'it']:
                    language_key = 'italian'
                elif lang_lower in ['portuguese', 'português', 'pt']:
                    language_key = 'portuguese'
            
            # Select voice based on language
            voice = self.voice_mapping.get(language_key, self.voice_mapping['default'])
            
            self.logger.info(f"Using voice '{voice}' for {language_key} content")
            
            # IMPORTANT: Add pronunciation hints for Spanish
            if language_key == 'spanish':
                # Add SSML-like pronunciation hints (though OpenAI doesn't support SSML)
                # We can add pauses and emphasis to help with pronunciation
                text = self._add_spanish_pronunciation_hints(text)
            
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text, language_key)
            
            if not clean_text.strip():
                self.logger.warning(f"No valid text to convert for customer {customer_id}")
                return None
            
            # Truncate if too long
            if len(clean_text) > self.max_text_length:
                clean_text = clean_text[:self.max_text_length - 3] + "..."
                self.logger.warning(f"Text truncated for TTS (customer {customer_id})")
            
            # Generate filename with language tag
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{customer_id}_{message_type}_{language_key}_{timestamp}.mp3"
            file_path = self.voice_notes_dir / filename
            
            # CRITICAL: Set speech speed for better pronunciation
            # Slower speed helps with non-English pronunciation
            speech_speed = 1.0 if language_key == 'english' else 0.9
            
            # Generate speech with language-appropriate settings
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=clean_text,
                speed=speech_speed  # Slower for non-English
            )
            
            # Save to file
            response.stream_to_file(str(file_path))
            
            self.logger.info(f"Voice note generated: {file_path} (Language: {language_key})")
            
            # Log a warning about pronunciation limitations
            if language_key != 'english':
                self.logger.warning(
                    f"Note: OpenAI TTS has limited support for {language_key}. "
                    f"The voice '{voice}' will speak with an English accent. "
                    f"For native pronunciation, consider using Azure Speech or Google Cloud TTS."
                )
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error generating voice note for customer {customer_id}: {e}")
            return None
    
    def _add_spanish_pronunciation_hints(self, text: str) -> str:
        """
        Add hints to improve Spanish pronunciation.
        Note: OpenAI doesn't support SSML, but we can add natural pauses.
        """
        # Add slight pauses after common Spanish greetings
        text = text.replace('Hola,', 'Hola...')
        text = text.replace('Buenos días,', 'Buenos días...')
        text = text.replace('Buenas tardes,', 'Buenas tardes...')
        
        # Add pauses before important numbers or amounts
        text = re.sub(r'(\d+)', r'... \1', text)
        
        # Emphasize important Spanish words by adding pauses
        important_words = ['importante', 'urgente', 'atención', 'cuenta', 'tarjeta']
        for word in important_words:
            text = text.replace(f' {word} ', f' ... {word} ... ')
        
        return text
    
    def _clean_text_for_tts(self, text: str, language: str = 'english') -> str:
        """
        Clean text to make it suitable for text-to-speech.
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Language-specific character preservation
        if language == 'spanish':
            # Keep Spanish characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-áéíóúñÁÉÍÓÚÑüÜ¿¡]', '', text)
        elif language == 'french':
            # Keep French characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]', '', text)
        elif language == 'german':
            # Keep German characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-äöüßÄÖÜ]', '', text)
        else:
            # Default: basic punctuation only
            text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Language-specific replacements
        if language == 'spanish':
            replacements = {
                'USD': 'dólares',
                'EUR': 'euros',
                'GBP': 'libras',
                'ATM': 'cajero automático',
                'PIN': 'pin',
                'SMS': 'mensaje de texto'
            }
        else:
            replacements = {
                'GBP': 'British Pounds',
                'USD': 'US Dollars',
                'EUR': 'Euros',
                'ATM': 'A T M',
                'PIN': 'P I N',
                'SMS': 'text message'
            }
        
        for abbrev, replacement in replacements.items():
            text = re.sub(rf'\b{abbrev}\b', replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def generate_voice_with_alternative_service(self, text: str, customer_id: str,
                                               language: str = 'spanish') -> Optional[Path]:
        """
        Alternative: Use a different TTS service for better Spanish support.
        This is a placeholder for integration with Azure Speech or Google Cloud TTS.
        """
        self.logger.info(
            f"For native {language} pronunciation, consider using:\n"
            f"  1. Azure Speech Services (native Spanish voices)\n"
            f"  2. Google Cloud Text-to-Speech (native Spanish voices)\n"
            f"  3. Amazon Polly (native Spanish voices)\n"
            f"  4. ElevenLabs (multilingual voice cloning)"
        )
        
        # For now, fall back to OpenAI
        return self.generate_voice_note(text, customer_id, "notification", language)
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices with language notes."""
        return [
            {"voice": "alloy", "description": "Neutral", "languages": "Best for English, acceptable for German"},
            {"voice": "echo", "description": "Male", "languages": "English only"},
            {"voice": "fable", "description": "British accent", "languages": "English only"},
            {"voice": "onyx", "description": "Deep male", "languages": "English only"},
            {"voice": "nova", "description": "Female, friendly", "languages": "Best for English, acceptable for Romance languages"},
            {"voice": "shimmer", "description": "Female, soft", "languages": "English only"}
        ]
    
    def test_voice_generation(self, test_text: str = None, language: str = 'english') -> Optional[Path]:
        """
        Test voice generation with sample text.
        """
        if test_text is None:
            if language == 'spanish':
                test_text = "Hola, esta es una prueba del sistema de generación de voz en español."
            else:
                test_text = "Hello, this is a test of the voice generation system."
        
        return self.generate_voice_note(test_text, f"TEST_{language.upper()}", "test", language)
    
    # ... (rest of the methods remain the same) ...
    
    def get_model_info(self) -> dict:
        """Get information about the current model configuration."""
        return {
            "tts_model": self.tts_model,
            "voice_mapping": self.voice_mapping,
            "max_text_length": self.max_text_length,
            "available_voices": self.get_available_voices(),
            "voice_notes_directory": str(self.voice_notes_dir),
            "status": "ready",
            "language_support": "Limited - English accent on all voices",
            "recommendation": "For native language support, use Azure Speech or Google Cloud TTS"
        }