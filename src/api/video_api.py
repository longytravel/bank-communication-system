"""
D-ID Video Generation API with Multi-Language Support
Handles video generation for personalized banking messages in multiple languages.
"""

import logging
import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict, List
import sys
import os
import re

sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_key, get_directory

class VideoAPI:
    """D-ID API wrapper for video generation with multi-language support."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get API key from config
        api_key = get_api_key('did')  # This will look for DID_API_KEY
        if not api_key:
            self.logger.warning("D-ID API key not found. Video generation will be disabled.")
            self.enabled = False
            return
        
        self.enabled = True
        self.api_key = api_key
        self.base_url = "https://api.d-id.com"
        
        # Video output directory
        self.video_dir = get_directory('video_messages') if get_directory else Path("data/video_messages")
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        # Language configuration with D-ID voice mappings
        self.language_config = {
            'english': {
                'code': 'en',
                'provider': 'microsoft',
                'voices': {
                    'female': 'en-US-JennyNeural',
                    'male': 'en-US-GuyNeural',
                    'professional': 'en-US-AriaNeural'
                },
                'default_voice': 'en-US-JennyNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'spanish': {
                'code': 'es',
                'provider': 'microsoft',
                'voices': {
                    'female': 'es-ES-ElviraNeural',
                    'male': 'es-ES-AlvaroNeural',
                    'professional': 'es-MX-DaliaNeural'
                },
                'default_voice': 'es-ES-ElviraNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'french': {
                'code': 'fr',
                'provider': 'microsoft',
                'voices': {
                    'female': 'fr-FR-DeniseNeural',
                    'male': 'fr-FR-HenriNeural',
                    'professional': 'fr-FR-BrigitteNeural'
                },
                'default_voice': 'fr-FR-DeniseNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'german': {
                'code': 'de',
                'provider': 'microsoft',
                'voices': {
                    'female': 'de-DE-KatjaNeural',
                    'male': 'de-DE-ConradNeural',
                    'professional': 'de-DE-AmalaNeural'
                },
                'default_voice': 'de-DE-KatjaNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'italian': {
                'code': 'it',
                'provider': 'microsoft',
                'voices': {
                    'female': 'it-IT-ElsaNeural',
                    'male': 'it-IT-DiegoNeural',
                    'professional': 'it-IT-IsabellaNeural'
                },
                'default_voice': 'it-IT-ElsaNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'portuguese': {
                'code': 'pt',
                'provider': 'microsoft',
                'voices': {
                    'female': 'pt-BR-FranciscaNeural',
                    'male': 'pt-BR-AntonioNeural',
                    'professional': 'pt-PT-RaquelNeural'
                },
                'default_voice': 'pt-BR-FranciscaNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'polish': {
                'code': 'pl',
                'provider': 'microsoft',
                'voices': {
                    'female': 'pl-PL-AgnieszkaNeural',
                    'male': 'pl-PL-MarekNeural',
                    'professional': 'pl-PL-ZofiaNeural'
                },
                'default_voice': 'pl-PL-ZofiaNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'urdu': {
                'code': 'ur',
                'provider': 'microsoft',
                'voices': {
                    'female': 'ur-PK-UzmaNeural',
                    'male': 'ur-PK-AsadNeural',
                    'professional': 'ur-PK-UzmaNeural'
                },
                'default_voice': 'ur-PK-UzmaNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'mandarin': {
                'code': 'zh',
                'provider': 'microsoft',
                'voices': {
                    'female': 'zh-CN-XiaoxiaoNeural',
                    'male': 'zh-CN-YunxiNeural',
                    'professional': 'zh-CN-XiaoyiNeural'
                },
                'default_voice': 'zh-CN-XiaoxiaoNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'arabic': {
                'code': 'ar',
                'provider': 'microsoft',
                'voices': {
                    'female': 'ar-SA-ZariyahNeural',
                    'male': 'ar-SA-HamedNeural',
                    'professional': 'ar-AE-FatimaNeural'
                },
                'default_voice': 'ar-SA-ZariyahNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'hindi': {
                'code': 'hi',
                'provider': 'microsoft',
                'voices': {
                    'female': 'hi-IN-SwaraNeural',
                    'male': 'hi-IN-MadhurNeural',
                    'professional': 'hi-IN-SwaraNeural'
                },
                'default_voice': 'hi-IN-SwaraNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            },
            'japanese': {
                'code': 'ja',
                'provider': 'microsoft',
                'voices': {
                    'female': 'ja-JP-NanamiNeural',
                    'male': 'ja-JP-KeitaNeural',
                    'professional': 'ja-JP-AoiNeural'
                },
                'default_voice': 'ja-JP-NanamiNeural',
                'avatars': {
                    'professional': 'amy-jcwCkr1grs',
                    'friendly': 'josh-j2tVIcLCVPINZ',
                    'senior': 'alex-KZmQ0KniB7E'
                }
            }
        }
        
        # Default configuration
        self.default_presenter = "amy-jcwCkr1grs"  # Professional female avatar
        self.default_language = 'english'
        
        self.logger.info("Video API initialized successfully with multi-language support")
    
    def detect_language(self, text: str, customer_data: Dict = None) -> str:
        """
        Detect language from text or customer data.
        
        Args:
            text: Text to analyze for language
            customer_data: Customer data dictionary that may contain language preference
            
        Returns:
            Detected language key (e.g., 'spanish', 'french')
        """
        # First check if customer data has explicit language field
        if customer_data:
            # Check for explicit language field in customer data
            customer_language = customer_data.get('preferred_language', '').lower()
            if not customer_language:
                customer_language = customer_data.get('language', '').lower()
            
            if customer_language:
                # Map common language codes/names to our keys                
                language_mapping = {
                    'en': 'english', 'eng': 'english', 'english': 'english',
                    'es': 'spanish', 'esp': 'spanish', 'spanish': 'spanish', 'español': 'spanish',
                    'fr': 'french', 'fra': 'french', 'french': 'french', 'français': 'french',
                    'de': 'german', 'ger': 'german', 'german': 'german', 'deutsch': 'german',
                    'it': 'italian', 'ita': 'italian', 'italian': 'italian', 'italiano': 'italian',
                    'pt': 'portuguese', 'por': 'portuguese', 'portuguese': 'portuguese', 'português': 'portuguese',
                    'pl': 'polish', 'pol': 'polish', 'polish': 'polish', 'polski': 'polish',  # NEW
                    'ur': 'urdu', 'urd': 'urdu', 'urdu': 'urdu', 'اردو': 'urdu',  # NEW
                    'zh': 'mandarin', 'chi': 'mandarin', 'chinese': 'mandarin', 'mandarin': 'mandarin', '中文': 'mandarin',
                    'ar': 'arabic', 'ara': 'arabic', 'arabic': 'arabic', 'عربي': 'arabic',
                    'hi': 'hindi', 'hin': 'hindi', 'hindi': 'hindi', 'हिंदी': 'hindi',
                    'ja': 'japanese', 'jpn': 'japanese', 'japanese': 'japanese', '日本語': 'japanese'
                }
                
                detected = language_mapping.get(customer_language, '')
                if detected:
                    self.logger.info(f"Language detected from customer data: {detected}")
                    return detected
        
        # Fallback to text-based detection
        text_lower = text.lower() if text else ''
        
        # Language detection patterns
        language_patterns = {
            'polish': {
                'keywords': ['dzień dobry', 'dziękuję', 'pan', 'pani', 'konto', 'bank', 
                        'proszę', 'jest', 'mieć', 'pieniądze', 'karta', 'kredyt'],
                'patterns': [r'\b(ą|ć|ę|ł|ń|ó|ś|ź|ż)\b', r'\b(się|jest|będzie)\b']
            },
            'urdu': {
                'keywords': ['شکریہ', 'جناب', 'محترمہ', 'کھاتہ', 'بینک', 
                        'آپ', 'ہے', 'پیسے', 'کارڈ'],
                'patterns': [r'[\u0600-\u06ff\u0750-\u077f]']  # Arabic/Urdu script
            },
      
            'spanish': {
                'keywords': ['hola', 'gracias', 'señor', 'señora', 'cuenta', 'banco', 'usted', 
                           'está', 'día', 'por favor', 'dinero', 'tarjeta', 'préstamo'],
                'patterns': [r'\b(está|están|estás)\b', r'\b(señor|señora)\b', r'\¿', r'\¡']
            },
            'french': {
                'keywords': ['bonjour', 'merci', 'monsieur', 'madame', 'compte', 'banque', 
                           'vous', 'être', 'avoir', 'argent', 'carte', 'prêt'],
                'patterns': [r'\b(être|êtes)\b', r'\b(à|è|é|ê|ç)\b']
            },
            'german': {
                'keywords': ['hallo', 'danke', 'herr', 'frau', 'konto', 'bank', 'sie', 
                           'ist', 'haben', 'geld', 'karte', 'kredit'],
                'patterns': [r'\b(über|für|können)\b', r'ß', r'ä', r'ö', r'ü']
            },
            'italian': {
                'keywords': ['ciao', 'grazie', 'signore', 'signora', 'conto', 'banca', 
                           'lei', 'essere', 'avere', 'denaro', 'carta'],
                'patterns': [r'\b(è|à|ò|ù)\b']
            },
            'portuguese': {
                'keywords': ['olá', 'obrigado', 'senhor', 'senhora', 'conta', 'banco', 
                           'você', 'estar', 'ter', 'dinheiro', 'cartão'],
                'patterns': [r'\b(ção|ções|ão)\b', r'ã', r'õ']
            },
            'mandarin': {
                'patterns': [r'[\u4e00-\u9fff]']  # Chinese characters
            },
            'arabic': {
                'patterns': [r'[\u0600-\u06ff]']  # Arabic characters
            },
            'hindi': {
                'patterns': [r'[\u0900-\u097f]']  # Devanagari script
            },
            'japanese': {
                'patterns': [r'[\u3040-\u309f]', r'[\u30a0-\u30ff]', r'[\u4e00-\u9faf]']  # Hiragana, Katakana, Kanji
            }
        }
        
        # Count matches for each language
        language_scores = {}
        
        for language, config in language_patterns.items():
            score = 0
            
            # Check keywords
            if 'keywords' in config:
                for keyword in config['keywords']:
                    if keyword in text_lower:
                        score += 2  # Keywords are strong indicators
            
            # Check patterns
            if 'patterns' in config:
                for pattern in config['patterns']:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    score += len(matches)
            
            if score > 0:
                language_scores[language] = score
        
        # Return the language with highest score
        if language_scores:
            detected_language = max(language_scores, key=language_scores.get)
            self.logger.info(f"Language detected from text analysis: {detected_language} (score: {language_scores[detected_language]})")
            return detected_language
        
        # Default to English
        self.logger.info("No specific language detected, defaulting to English")
        return 'english'
    
    def get_voice_for_language(self, language: str, voice_type: str = 'professional', 
                              customer_data: Dict = None) -> str:
        """
        Get appropriate voice ID for the language and customer profile.
        
        Args:
            language: Language key (e.g., 'spanish')
            voice_type: Type of voice ('professional', 'friendly', 'male', 'female')
            customer_data: Customer data for personalization
            
        Returns:
            Voice ID string for D-ID API
        """
        lang_config = self.language_config.get(language, self.language_config['english'])
        
        # Determine voice based on customer data if available
        if customer_data:
            age = customer_data.get('age', 40)
            gender_preference = customer_data.get('preferred_voice_gender', '').lower()
            
            # Age-based voice selection
            if age < 35:
                voice_type = 'friendly' if 'friendly' in lang_config['voices'] else 'female'
            elif age > 60:
                voice_type = 'professional'
            
            # Gender preference override
            if gender_preference in ['male', 'female'] and gender_preference in lang_config['voices']:
                voice_type = gender_preference
        
        # Get the voice ID
        voice_id = lang_config['voices'].get(voice_type, lang_config['default_voice'])
        
        self.logger.info(f"Selected voice: {voice_id} for language: {language}, type: {voice_type}")
        return voice_id
    
    def get_avatar_for_customer(self, customer_data: Dict = None, language: str = 'english') -> str:
        """
        Select appropriate avatar based on customer profile.
        
        Args:
            customer_data: Customer data dictionary
            language: Language for the video
            
        Returns:
            Avatar ID for D-ID API
        """
        lang_config = self.language_config.get(language, self.language_config['english'])
        
        if customer_data:
            # Check customer tier/value
            account_balance = customer_data.get('account_balance', 0)
            try:
                if isinstance(account_balance, str):
                    account_balance = float(account_balance.replace(',', '').replace('£', '').replace('$', ''))
                else:
                    account_balance = float(account_balance)
            except:
                account_balance = 0
            
            # High-value customers get senior avatar
            if account_balance >= 50000:
                avatar_type = 'senior'
            elif account_balance >= 25000:
                avatar_type = 'professional'
            else:
                avatar_type = 'friendly'
            
            avatar_id = lang_config['avatars'].get(avatar_type, self.default_presenter)
        else:
            avatar_id = self.default_presenter
        
        self.logger.info(f"Selected avatar: {avatar_id}")
        return avatar_id
    
    def generate_video_message(self, text: str, customer_id: str, 
                              message_type: str = "notification",
                              customer_data: Dict = None,
                              language: str = None) -> Optional[Path]:
        """
        Generate a video message from text with language support.
        
        Args:
            text: Text for the avatar to speak
            customer_id: Customer identifier for filename
            message_type: Type of message
            customer_data: Full customer data including language preference
            language: Override language (if not provided, will auto-detect)
            
        Returns:
            Path to the generated video file, or None if failed
        """
        if not self.enabled:
            self.logger.warning("Video API not enabled - no API key configured")
            return None
            
        try:
            # Detect or use provided language
            if not language:
                language = self.detect_language(text, customer_data)
            
            self.logger.info(f"Generating video for customer {customer_id} in {language}")
            
            # Clean and prepare text
            clean_text = self._prepare_text_for_language(text, language)
            if len(clean_text) > 500:
                clean_text = clean_text[:497] + "..."
            
            # Get voice and avatar
            voice_id = self.get_voice_for_language(language, customer_data=customer_data)
            avatar_id = self.get_avatar_for_customer(customer_data, language)
            
            # Step 1: Create the talk
            talk_id = self._create_talk(clean_text, voice_id, avatar_id, language)
            if not talk_id:
                return None
            
            # Step 2: Wait for video to be ready
            video_url = self._wait_for_video(talk_id)
            if not video_url:
                return None
            
            # Step 3: Download the video
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{customer_id}_{message_type}_{language}_{timestamp}.mp4"
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
    
    def _prepare_text_for_language(self, text: str, language: str) -> str:
        """
        Prepare text for specific language requirements.
        
        Args:
            text: Original text
            language: Target language
            
        Returns:
            Prepared text
        """
        # Language-specific text preparation
        if language == 'arabic':
            # Arabic reads right-to-left, might need special handling
            text = text.strip()
        elif language in ['mandarin', 'japanese']:
            # Asian languages might need different punctuation handling
            text = text.replace('...', '。。。')
        
        # General cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _create_talk(self, text: str, voice_id: str, avatar_id: str, language: str) -> Optional[str]:
        """Create a talk with D-ID API with language support."""
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get language configuration
        lang_config = self.language_config.get(language, self.language_config['english'])
        
        # Build payload with correct avatar URL format
        payload = {
            "source_url": "https://create-images-results.d-id.com/api_docs/assets/noelle.jpeg",
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": lang_config['provider'],
                    "voice_id": voice_id
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.5
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
                self.logger.info(f"Talk created: {talk_id} in {language}")
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
    
    def generate_video_batch(self, video_requests: List[Dict]) -> Dict[str, Optional[Path]]:
        """
        Generate multiple videos efficiently with language support.
        
        Args:
            video_requests: List of dicts with 'text', 'customer_id', 'message_type', 'customer_data'
            
        Returns:
            Dict mapping customer_id to file path (or None if failed)
        """
        results = {}
        
        self.logger.info(f"Generating batch of {len(video_requests)} videos")
        
        for request in video_requests:
            customer_id = request.get('customer_id')
            text = request.get('text', '')
            message_type = request.get('message_type', 'notification')
            customer_data = request.get('customer_data', {})
            language = request.get('language')  # Optional override
            
            file_path = self.generate_video_message(
                text, customer_id, message_type, 
                customer_data=customer_data,
                language=language
            )
            results[customer_id] = file_path
            
            # Delay between videos to avoid rate limits
            time.sleep(1)
        
        success_count = sum(1 for path in results.values() if path is not None)
        self.logger.info(f"Generated {success_count}/{len(video_requests)} videos successfully")
        
        return results
    
    def test_video_generation(self, language: str = None) -> Optional[Path]:
        """
        Test video generation with sample text in specified language.
        
        Args:
            language: Language to test (if None, tests English)
            
        Returns:
            Path to test video file or None if failed
        """
        test_messages = {
            'english': "Hello, this is a test of our video banking system. Your account is in good standing.",
            'spanish': "Hola, esta es una prueba de nuestro sistema bancario de video. Su cuenta está en buen estado.",
            'french': "Bonjour, ceci est un test de notre système bancaire vidéo. Votre compte est en règle.",
            'german': "Hallo, dies ist ein Test unseres Video-Banking-Systems. Ihr Konto ist in gutem Zustand.",
            'italian': "Ciao, questo è un test del nostro sistema bancario video. Il tuo account è in regola.",
            'portuguese': "Olá, este é um teste do nosso sistema bancário de vídeo. Sua conta está em dia.",
            'mandarin': "您好，这是我们视频银行系统的测试。您的账户状态良好。",
            'arabic': "مرحبا، هذا اختبار لنظامنا المصرفي بالفيديو. حسابك في وضع جيد.",
            'hindi': "नमस्ते, यह हमारे वीडियो बैंकिंग सिस्टम का परीक्षण है। आपका खाता अच्छी स्थिति में है।",
            'japanese': "こんにちは、これは私たちのビデオバンキングシステムのテストです。あなたのアカウントは良好な状態です。"
        }
        
        if not language:
            language = 'english'
        
        test_text = test_messages.get(language, test_messages['english'])
        
        return self.generate_video_message(
            test_text,
            f"TEST_{language.upper()}",
            "test",
            language=language
        )
    
    def get_video_stats(self) -> dict:
        """Get statistics about generated videos."""
        if not self.enabled:
            return {
                "enabled": False,
                "total_files": 0,
                "total_size_mb": 0,
                "videos_by_language": {}
            }
            
        video_files = list(self.video_dir.glob("*.mp4"))
        
        total_files = len(video_files)
        total_size = sum(f.stat().st_size for f in video_files if f.exists())
        
        # Count videos by language
        videos_by_language = {}
        for file in video_files:
            # Extract language from filename if present
            parts = file.stem.split('_')
            for part in parts:
                if part in self.language_config:
                    videos_by_language[part] = videos_by_language.get(part, 0) + 1
                    break
        
        return {
            "enabled": True,
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "videos_generated": total_files,
            "videos_by_language": videos_by_language,
            "supported_languages": list(self.language_config.keys())
        }
    
    def cleanup_old_videos(self, days_old: int = 30) -> int:
        """
        Clean up videos older than specified days.
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        if not self.enabled:
            return 0
            
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for file in self.video_dir.glob("*.mp4"):
            if file.stat().st_mtime < cutoff_time:
                try:
                    file.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old video: {file.name}")
                except Exception as e:
                    self.logger.error(f"Error deleting {file.name}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old videos")
        return deleted_count
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages with details.
        
        Returns:
            List of language dictionaries with name, code, and voice options
        """
        languages = []
        for lang_key, config in self.language_config.items():
            languages.append({
                'key': lang_key,
                'code': config['code'],
                'name': lang_key.title(),
                'voices_available': len(config['voices']),
                'default_voice': config['default_voice']
            })
        return languages