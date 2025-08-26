"""
Remove emojis from logging to fix Windows console issues
"""

from pathlib import Path

def remove_emojis_from_logs():
    """Remove emoji characters that break Windows console."""
    
    print("Removing emojis from logging...")
    
    # File to fix
    video_rules_file = Path("src/business_rules/video_rules.py")
    
    if video_rules_file.exists():
        content = video_rules_file.read_text(encoding='utf-8')
        
        # Replace emojis in logging statements
        replacements = [
            ('self.logger.info(f"✅', 'self.logger.info(f"[OK]'),
            ('self.logger.info(f"❌', 'self.logger.info(f"[X]'),
            ('self.logger.info(f"🔍', 'self.logger.info(f"[DEBUG]'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Save the file
        video_rules_file.write_text(content, encoding='utf-8')
        print(f"✅ Fixed: {video_rules_file}")
    
    return True

if __name__ == "__main__":
    remove_emojis_from_logs()
    print("\n✅ Emoji logging fixed!")
    print("Now run: python test_letter_rewrite.py")