import sys
sys.path.append('src')

from api.api_manager import APIManager

print("Testing Video through API Manager...")
print("-" * 40)

try:
    api = APIManager()
    print("✅ API Manager initialized with video support")
    
    print("\n🎬 Generating video through API Manager...")
    result = api.generate_video_message(
        "Hello Sarah, your account balance is healthy and you have been pre-approved for our premium card.",
        "CUST001",
        "notification"
    )
    
    if result:
        print(f"✅ Video created successfully!")
        print(f"📁 Saved to: {result}")
        print(f"📊 File size: {result.stat().st_size / 1024:.1f} KB")
    else:
        print("❌ Failed to generate video")
        
except Exception as e:
    print(f"❌ Error: {e}")
