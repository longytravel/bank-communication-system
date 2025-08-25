"""
Test Spanish video generation for Maria
"""

import sys
sys.path.append('src')

from api.api_manager import APIManager
from pathlib import Path

print("=" * 60)
print("TESTING SPANISH VIDEO GENERATION")
print("=" * 60)

# Maria's test data
maria_data = {
    'customer_id': 'MARIA_TEST',
    'name': 'Maria Garcia',
    'preferred_language': 'Spanish',
    'account_balance': 25000,
    'age': 35
}

# Spanish test message
spanish_text = "Hola Maria, su cuenta está en excelente estado y ha sido preaprobada para nuestra tarjeta premium."
english_text = "Hello Maria, your account is in excellent standing and you've been pre-approved for our premium card."

try:
    # Initialize API manager
    print("\n1. Initializing API Manager...")
    api_manager = APIManager()
    print("   ✅ API Manager ready")
    
    # Check if video API is available
    if api_manager.video:
        print("   ✅ Video API is initialized")
        
        # Test 1: Generate English video
        print("\n2. Testing ENGLISH video generation...")
        english_result = api_manager.generate_video_message(
            english_text,
            "MARIA_TEST_EN",
            "notification",
            customer_data=maria_data
        )
        
        if english_result and english_result.exists():
            print(f"   ✅ English video created: {english_result.name}")
            print(f"   📁 Size: {english_result.stat().st_size / 1024:.1f} KB")
        else:
            print("   ❌ English video generation failed")
        
        # Test 2: Generate Spanish video
        print("\n3. Testing SPANISH video generation...")
        spanish_result = api_manager.generate_video_message(
            spanish_text,
            "MARIA_TEST_ES", 
            "notification",
            customer_data=maria_data
        )
        
        if spanish_result and spanish_result.exists():
            print(f"   ✅ Spanish video created: {spanish_result.name}")
            print(f"   📁 Size: {spanish_result.stat().st_size / 1024:.1f} KB")
        else:
            print("   ❌ Spanish video generation failed")
            print("   This might be the issue - D-ID API may have problems with Spanish text")
        
        # Check what videos exist for Maria
        print("\n4. Checking existing Maria videos...")
        video_dir = Path("data/video_messages")
        if video_dir.exists():
            maria_videos = list(video_dir.glob("*MARIA*"))
            if maria_videos:
                print(f"   Found {len(maria_videos)} Maria-related videos:")
                for video in maria_videos:
                    print(f"   - {video.name} ({video.stat().st_size / 1024:.1f} KB)")
            else:
                print("   No Maria videos found in directory")
        
    else:
        print("   ❌ Video API not initialized")
        print("   Check if DID_API_KEY is set in your .env file")
        
except Exception as e:
    print(f"\n❌ Error during test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("-" * 60)
print("If Spanish video failed but English worked:")
print("  → D-ID API might have issues with Spanish text")
print("  → We may need to use English for video scripts")
print("\nIf both failed:")
print("  → Check your DID_API_KEY in .env file")
print("  → Check your D-ID account has credits")
print("=" * 60)