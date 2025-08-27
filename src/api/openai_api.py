"""
OpenAI API Integration - FIXED FOR MULTILINGUAL SUPPORT
This version properly handles Spanish, Polish, Urdu and other languages.
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
    OpenAI API wrapper for voice generation with PROPER multilingual support.
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
            'polish': 'nova',    # NEW - Nova handles European languages reasonably
            'urdu': 'nova',      # NEW - Nova is most versatile for non-Latin scripts
            'mandarin': 'nova',
            'arabic': 'nova',
            'hindi': 'nova',
            'japanese': 'nova',
            'default': 'nova'
        }
        
        # Voice notes directory
        self.voice_notes_dir = get_directory('voice_notes')
        
        self.logger.info("OpenAI API initialized with multilingual support")

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
                elif lang_lower in ['polish', 'polski', 'pl']:  # NEW
                    language_key = 'polish'
                elif lang_lower in ['urdu', 'اردو', 'ur']:  # NEW
                    language_key = 'urdu'
                elif lang_lower in ['mandarin', 'chinese', 'zh', '中文']:
                    language_key = 'mandarin'
                elif lang_lower in ['arabic', 'عربي', 'ar']:
                    language_key = 'arabic'
                elif lang_lower in ['hindi', 'हिंदी', 'hi']:
                    language_key = 'hindi'
                elif lang_lower in ['japanese', '日本語', 'ja']:
                    language_key = 'japanese'
            
            # Select voice based on language
            voice = self.voice_mapping.get(language_key, self.voice_mapping['default'])
            
            self.logger.info(f"Using voice '{voice}' for {language_key} content")
            
            # Add pronunciation hints based on language
            if language_key == 'spanish':
                text = self._add_spanish_pronunciation_hints(text)
            elif language_key == 'polish':  # NEW
                text = self._add_polish_pronunciation_hints(text)
            elif language_key == 'urdu':  # NEW
                text = self._add_urdu_pronunciation_hints(text)
            
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
            if language_key == 'english':
                speech_speed = 1.0
            elif language_key in ['polish', 'urdu', 'arabic', 'mandarin', 'japanese']:
                speech_speed = 0.85  # Even slower for complex languages
            else:
                speech_speed = 0.9
            
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
            if language_key not in ['english', 'spanish', 'french']:
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
    
    def _add_polish_pronunciation_hints(self, text: str) -> str:
        """
        Add hints to improve Polish pronunciation.
        Polish has complex consonant clusters that need pauses.
        """
        # Add pauses after common Polish greetings
        text = text.replace('Dzień dobry,', 'Dzień dobry...')
        text = text.replace('Dobry wieczór,', 'Dobry wieczór...')
        text = text.replace('Szanowny Panie,', 'Szanowny Panie...')
        text = text.replace('Szanowna Pani,', 'Szanowna Pani...')
        
        # Polish-specific replacements for better pronunciation
        replacements = {
            'zł': 'złotych',
            'PLN': 'złotych',
            'PIN': 'pin',
            'SMS': 'es em es',
            'ATM': 'bankomat'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Add pauses around complex consonant clusters
        complex_words = ['proszę', 'dziękuję', 'przepraszam', 'szczególnie', 'przesłać']
        for word in complex_words:
            text = text.replace(f' {word} ', f' ... {word} ... ')
        
        return text
    
    def _add_urdu_pronunciation_hints(self, text: str) -> str:
        """
        Add hints for Urdu text pronunciation.
        Note: OpenAI TTS has very limited Urdu support.
        """
        # Warning about Urdu limitations
        self.logger.warning(
            "OpenAI TTS has very limited Urdu support. "
            "For proper Urdu pronunciation, use Azure Speech Services with Urdu voices "
            "or Google Cloud Text-to-Speech with Urdu support."
        )
        
        # If text contains Urdu script, consider transliteration
        if re.search(r'[\u0600-\u06ff\u0750-\u077f]', text):
            self.logger.info("Urdu script detected. Consider transliteration for better results.")
            # Add pauses for emphasis
            text = re.sub(r'([۔؟!])', r'\1 ... ', text)
        
        # Common Urdu banking terms (if transliterated)
        replacements = {
            'PIN': 'pin',
            'ATM': 'ay tee em',
            'SMS': 'es em es',
            'PKR': 'rupees'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _clean_text_for_tts(self, text: str, language: str = 'english') -> str:
        """
        Clean text to make it suitable for text-to-speech.
        Language-specific character preservation.
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
        elif language == 'italian':
            # Keep Italian characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-àèéìíòóùúÀÈÉÌÍÒÓÙÚ]', '', text)
        elif language == 'portuguese':
            # Keep Portuguese characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]', '', text)
        elif language == 'polish':  # NEW
            # Keep Polish characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', '', text)
        elif language == 'urdu':  # NEW
            # Keep Urdu/Arabic script characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-\u0600-\u06ff\u0750-\u077f۔؟]', '', text)
        elif language in ['mandarin', 'chinese']:
            # Keep Chinese characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-\u4e00-\u9fff，。！？；：、]', '', text)
        elif language == 'arabic':
            # Keep Arabic characters
            text = re.sub(r'[^\w\s.,!?;:\'\"-\u0600-\u06ff]', '', text)
        elif language == 'hindi':
            # Keep Devanagari script
            text = re.sub(r'[^\w\s.,!?;:\'\"-\u0900-\u097f।]', '', text)
        elif language == 'japanese':
            # Keep Japanese characters (Hiragana, Katakana, Kanji)
            text = re.sub(r'[^\w\s.,!?;:\'\"-\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf。、！？]', '', text)
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
        elif language == 'polish':  # NEW
            replacements = {
                'USD': 'dolarów',
                'EUR': 'euro',
                'GBP': 'funtów',
                'ATM': 'bankomat',
                'PIN': 'kod pin',
                'SMS': 'wiadomość tekstowa'
            }
        elif language == 'french':
            replacements = {
                'USD': 'dollars',
                'EUR': 'euros',
                'GBP': 'livres sterling',
                'ATM': 'distributeur automatique',
                'PIN': 'code pin',
                'SMS': 'texto'
            }
        elif language == 'german':
            replacements = {
                'USD': 'Dollar',
                'EUR': 'Euro',
                'GBP': 'Pfund',
                'ATM': 'Geldautomat',
                'PIN': 'PIN-Code',
                'SMS': 'SMS-Nachricht'
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
        Alternative: Use a different TTS service for better language support.
        This is a placeholder for integration with Azure Speech or Google Cloud TTS.
        """
        self.logger.info(
            f"For native {language} pronunciation, consider using:\n"
            f"  1. Azure Speech Services (native {language} voices)\n"
            f"  2. Google Cloud Text-to-Speech (native {language} voices)\n"
            f"  3. Amazon Polly (native {language} voices)\n"
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
            {"voice": "nova", "description": "Female, friendly", "languages": "Best for English, acceptable for Romance languages, Polish, Urdu"},
            {"voice": "shimmer", "description": "Female, soft", "languages": "English only"}
        ]
    
    def test_voice_generation(self, test_text: str = None, language: str = 'english') -> Optional[Path]:
        """
        Test voice generation with sample text in different languages.
        """
        if test_text is None:
            test_texts = {
                'english': "Hello, this is a test of the voice generation system.",
                'spanish': "Hola, esta es una prueba del sistema de generación de voz en español.",
                'french': "Bonjour, ceci est un test du système de génération vocale.",
                'german': "Hallo, dies ist ein Test des Sprachgenerierungssystems.",
                'italian': "Ciao, questo è un test del sistema di generazione vocale.",
                'portuguese': "Olá, este é um teste do sistema de geração de voz.",
                'polish': "Dzień dobry, to jest test systemu generowania głosu w języku polskim.",
                'urdu': "یہ آواز کی تخلیق کے نظام کا ٹیسٹ ہے۔",
                'mandarin': "你好，这是语音生成系统的测试。",
                'arabic': "مرحبا، هذا اختبار لنظام توليد الصوت.",
                'hindi': "नमस्ते, यह वॉयस जेनरेशन सिस्टम का परीक्षण है।",
                'japanese': "こんにちは、これは音声生成システムのテストです。"
            }
            test_text = test_texts.get(language, test_texts['english'])
        
        return self.generate_voice_note(test_text, f"TEST_{language.upper()}", "test", language)
    
    def get_model_info(self) -> dict:
        """Get information about the current model configuration."""
        return {
            "tts_model": self.tts_model,
            "voice_mapping": self.voice_mapping,
            "max_text_length": self.max_text_length,
            "available_voices": self.get_available_voices(),
            "voice_notes_directory": str(self.voice_notes_dir),
            "status": "ready",
            "supported_languages": list(self.voice_mapping.keys()),
            "language_support": "Limited - English accent on most voices",
            "polish_support": "Basic - English accent pronunciation",
            "urdu_support": "Very Limited - Consider Azure Speech or Google Cloud TTS",
            "recommendation": "For native language support, use Azure Speech or Google Cloud TTS"
        }