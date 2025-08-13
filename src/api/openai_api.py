"""
OpenAI API Integration
Handles OpenAI API calls for voice generation and additional AI features.
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
    OpenAI API wrapper for voice generation and other features.
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
        self.default_voice = "nova"  # Professional, friendly voice
        self.max_text_length = 4096  # OpenAI TTS limit
        
        # Voice notes directory
        self.voice_notes_dir = get_directory('voice_notes')
        
        self.logger.info("OpenAI API initialized successfully")
    
    def generate_voice_note(self, text: str, customer_id: str, 
                          message_type: str = "notification") -> Optional[Path]:
        """
        Generate a voice note from text using OpenAI TTS.
        
        Args:
            text: Text to convert to speech
            customer_id: Customer identifier for filename
            message_type: Type of message (notification, alert, etc.)
            
        Returns:
            Path to the generated audio file, or None if failed
        """
        try:
            self.logger.info(f"Generating voice note for customer {customer_id}")
            
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            if not clean_text.strip():
                self.logger.warning(f"No valid text to convert for customer {customer_id}")
                return None
            
            # Truncate if too long
            if len(clean_text) > self.max_text_length:
                clean_text = clean_text[:self.max_text_length - 3] + "..."
                self.logger.warning(f"Text truncated for TTS (customer {customer_id})")
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{customer_id}_{message_type}_{timestamp}.mp3"
            file_path = self.voice_notes_dir / filename
            
            # Generate speech
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=self.default_voice,
                input=clean_text
            )
            
            # Save to file
            response.stream_to_file(str(file_path))
            
            self.logger.info(f"Voice note generated: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error generating voice note for customer {customer_id}: {e}")
            return None
    
    def generate_voice_notes_batch(self, voice_requests: list) -> dict:
        """
        Generate multiple voice notes efficiently.
        
        Args:
            voice_requests: List of dicts with 'text', 'customer_id', 'message_type'
            
        Returns:
            Dict mapping customer_id to file path (or None if failed)
        """
        results = {}
        
        self.logger.info(f"Generating batch of {len(voice_requests)} voice notes")
        
        for request in voice_requests:
            customer_id = request.get('customer_id')
            text = request.get('text', '')
            message_type = request.get('message_type', 'notification')
            
            file_path = self.generate_voice_note(text, customer_id, message_type)
            results[customer_id] = file_path
            
            # Small delay to avoid rate limits
            time.sleep(0.1)
        
        success_count = sum(1 for path in results.values() if path is not None)
        self.logger.info(f"Generated {success_count}/{len(voice_requests)} voice notes successfully")
        
        return results
    
    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text to make it suitable for text-to-speech.
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove emojis and special characters that TTS can't handle
        # Keep basic punctuation for natural speech
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Replace some banking abbreviations for better pronunciation
        replacements = {
            'GBP': 'British Pounds',
            'USD': 'US Dollars',
            'EUR': 'Euros',
            'ATM': 'A T M',
            'PIN': 'P I N',
            'API': 'A P I',
            'SMS': 'text message',
            'QR': 'Q R',
            'ID': 'I D'
        }
        
        for abbrev, replacement in replacements.items():
            text = re.sub(rf'\b{abbrev}\b', replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices."""
        return [
            "alloy",    # Neutral
            "echo",     # Male
            "fable",    # British accent
            "onyx",     # Deep male
            "nova",     # Female, friendly (default)
            "shimmer"   # Female, soft
        ]
    
    def test_voice_generation(self, test_text: str = "Hello, this is a test of the voice generation system.") -> Optional[Path]:
        """
        Test voice generation with sample text.
        
        Args:
            test_text: Text to use for testing
            
        Returns:
            Path to test audio file or None if failed
        """
        return self.generate_voice_note(test_text, "TEST", "test")
    
    def get_voice_note_stats(self) -> dict:
        """Get statistics about generated voice notes."""
        voice_files = list(self.voice_notes_dir.glob("*.mp3"))
        
        total_files = len(voice_files)
        total_size = sum(f.stat().st_size for f in voice_files if f.exists())
        
        # Group by customer
        customer_counts = {}
        for file in voice_files:
            parts = file.stem.split('_')
            if len(parts) >= 2:
                customer_id = parts[0]
                customer_counts[customer_id] = customer_counts.get(customer_id, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "customers_with_voice_notes": len(customer_counts),
            "average_files_per_customer": round(total_files / max(len(customer_counts), 1), 1)
        }
    
    def cleanup_old_voice_notes(self, days_old: int = 30) -> int:
        """
        Clean up voice notes older than specified days.
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for file in self.voice_notes_dir.glob("*.mp3"):
            if file.stat().st_mtime < cutoff_time:
                try:
                    file.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old voice note: {file.name}")
                except Exception as e:
                    self.logger.error(f"Error deleting {file.name}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old voice notes")
        return deleted_count
    
    def get_model_info(self) -> dict:
        """Get information about the current model configuration."""
        return {
            "tts_model": self.tts_model,
            "default_voice": self.default_voice,
            "max_text_length": self.max_text_length,
            "available_voices": self.get_available_voices(),
            "voice_notes_directory": str(self.voice_notes_dir),
            "status": "ready"
        }