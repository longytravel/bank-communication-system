"""
SIMPLE TEST: Let's see what's actually happening with Spanish voice generation
Run this to diagnose the real issue
"""

import os
import sys
sys.path.append('src')

# Step 1: DELETE all existing Maria voice files
from pathlib import Path

voice_dir = Path("data/voice_notes")
if voice_dir.exists():
    # Delete ALL Maria files
    maria_files = list(voice_dir.glob("*MARIA*")) + list(voice_dir.glob("*CUST011*"))
    
    print("=" * 60)
    print("STEP 1: CLEANING UP OLD FILES")
    print("=" * 60)
    
    for file in maria_files:
        print(f"Deleting old file: {file.name}")
        file.unlink()
    
    print(f"Deleted {len(maria_files)} old Maria files")
    print()

# Step 2: Test DIRECT Spanish text generation
print("=" * 60)
print("STEP 2: DIRECT SPANISH TEXT TEST")
print("=" * 60)

# Import OpenAI directly - bypass everything else
from config import get_api_key, get_directory
import openai

api_key = get_api_key('openai')
if not api_key:
    print("❌ No OpenAI API key found!")
    exit()

client = openai.OpenAI(api_key=api_key)

# The EXACT Spanish text we want
spanish_text = "Hola María, soy Ana del Banco Resonance. Su cuenta está en excelente estado."

print(f"Spanish text to speak: {spanish_text}")
print()

# Generate THREE different versions to test
tests = [
    ("TEST1_NOVA", "nova", 1.0),
    ("TEST2_NOVA_SLOW", "nova", 0.85),
    ("TEST3_ALLOY", "alloy", 0.9)
]

voice_notes_dir = get_directory('voice_notes')

for test_name, voice, speed in tests:
    print(f"Generating {test_name} with voice={voice}, speed={speed}")
    
    try:
        # Direct OpenAI call - no wrapper functions
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=spanish_text,
            speed=speed
        )
        
        # Save the file
        output_file = voice_notes_dir / f"MARIA_{test_name}.mp3"
        response.stream_to_file(str(output_file))
        
        print(f"✅ Created: {output_file.name}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

print()
print("=" * 60)
print("STEP 3: TEST COMPLETE")
print("=" * 60)
print("Now go listen to the three files in data/voice_notes/:")
print("  - MARIA_TEST1_NOVA.mp3")
print("  - MARIA_TEST2_NOVA_SLOW.mp3")
print("  - MARIA_TEST3_ALLOY.mp3")
print()
print("WHAT DO YOU HEAR?")
print("  A) Spanish words with American accent (this is expected)")
print("  B) English translation (this would be weird)")
print("  C) Something else")
print()
print("Tell me what you hear and we'll fix it from there!")
print("=" * 60)