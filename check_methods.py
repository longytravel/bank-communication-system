"""
Check what methods exist in the VideoAPI class
"""
import sys
sys.path.append('src')

from api.video_api import VideoAPI
import inspect

print("=" * 60)
print("CHECKING VideoAPI CLASS METHODS")
print("=" * 60)

# Get all methods of VideoAPI class
methods = [method for method in dir(VideoAPI) if not method.startswith('__')]

print("\nPublic methods found in VideoAPI:")
for method in methods:
    if not method.startswith('_'):
        print(f"  - {method}")

print("\nPrivate methods found in VideoAPI:")
for method in methods:
    if method.startswith('_') and not method.startswith('__'):
        print(f"  - {method}")

print("\nLooking for _create_talk method:")
if '_create_talk' in methods:
    print("  ✅ _create_talk method EXISTS")
else:
    print("  ❌ _create_talk method is MISSING - this is the problem!")

print("\n" + "=" * 60)
print("The _create_talk method needs to be added to video_api.py")
print("=" * 60)