# test_video.py
import sys
from pathlib import Path
sys.path.append('src')

print("Testing D-ID Video Generation...")
print("-" * 40)

try:
    from api.video_api import VideoAPI
    print("✅ Video API module imported successfully")
    
    # Try to initialize
    video_api = VideoAPI()
    print("✅ Video API initialized")
    print(f"📁 Videos will be saved to: {video_api.video_dir}")
    
    # Generate a test video
    print("\n🎬 Generating test video...")
    print("This will use about 2 credits (10 seconds of video)")
    
    result = video_api.test_video_generation()
    
    if result and result.exists():
        print(f"✅ SUCCESS! Video saved to: {result}")
        print(f"📊 File size: {result.stat().st_size / 1024:.1f} KB")
    else:
        print("❌ Video generation failed")
        
except Exception as e:
    print(f"❌ Error: {e}")