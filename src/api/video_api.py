"""
D-ID Video Generation API
Handles video generation for personalized banking messages.
"""

import logging
import requests
import json
import time
from pathlib import Path
from typing import Optional
import sys
import os

sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_key, get_directory

class VideoAPI:
    """D-ID API wrapper for video generation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get API key from config
        api_key = get_api_key('did')  # This will look for DID_API_KEY
        if not api_key:
            raise ValueError("D-ID API key not found. Check your .env file.")
        
        self.api_key = api_key
        self.base_url = "https://api.d-id.com"
        
        # Video output directory (similar to voice_notes)
        self.video_dir = Path("data/video_messages")
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        # Use professional avatar
        self.default_presenter = "amy-jcwCkr1grs"  # Professional female
        
        self.logger.info("Video API initialized successfully")
    
    def generate_video_message(self, text: str, customer_id: str, 
                              message_type: str = "notification") -> Optional[Path]:
        """
        Generate a video message from text (similar to voice note).
        
        Args:
            text: Text for the avatar to speak
            customer_id: Customer identifier for filename
            message_type: Type of message
            
        Returns:
            Path to the generated video file, or None if failed
        """
        try:
            self.logger.info(f"Generating video for customer {customer_id}")
            
            # Clean and truncate text (D-ID has limits)
            clean_text = text.strip()
            if len(clean_text) > 500:  # Keep it short for demo
                clean_text = clean_text[:497] + "..."
            
            # Step 1: Create the talk
            talk_id = self._create_talk(clean_text)
            if not talk_id:
                return None
            
            # Step 2: Wait for video to be ready
            video_url = self._wait_for_video(talk_id)
            if not video_url:
                return None
            
            # Step 3: Download the video
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{customer_id}_{message_type}_{timestamp}.mp4"
            file_path = self.video_dir / filename
            
            response = requests.get(video_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"Video saved: {file_path}")
                return file_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating video for customer {customer_id}: {e}")
            return None
    
    def _create_talk(self, text: str) -> Optional[str]:
        """Create a talk with D-ID API."""
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple payload - using default avatar
        payload = {
            "source_url": f"https://d-id-public-bucket.s3.amazonaws.com/alice.jpg",
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-JennyNeural"  # Professional voice
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/talks",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                talk_id = result.get('id')
                self.logger.info(f"Talk created: {talk_id}")
                return talk_id
            else:
                self.logger.error(f"Failed to create talk: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating talk: {e}")
            return None
    
    def _wait_for_video(self, talk_id: str, max_wait: int = 60) -> Optional[str]:
        """Wait for video to be ready and get URL."""
        
        headers = {
            "Authorization": f"Basic {self.api_key}"
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/talks/{talk_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('status')
                    
                    if status == 'done':
                        video_url = result.get('result_url')
                        self.logger.info(f"Video ready: {talk_id}")
                        return video_url
                    elif status == 'error':
                        self.logger.error(f"Video generation failed: {result}")
                        return None
                    
                    # Still processing, wait a bit
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error checking video status: {e}")
                return None
        
        self.logger.error(f"Timeout waiting for video {talk_id}")
        return None
    
    def test_video_generation(self) -> Optional[Path]:
        """Test video generation with sample text."""
        return self.generate_video_message(
            "Hello, this is a test of our video banking system.",
            "TEST",
            "test"
        )
    
    def get_video_stats(self) -> dict:
        """Get statistics about generated videos (like voice notes)."""
        video_files = list(self.video_dir.glob("*.mp4"))
        
        total_files = len(video_files)
        total_size = sum(f.stat().st_size for f in video_files if f.exists())
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "videos_generated": total_files
        }