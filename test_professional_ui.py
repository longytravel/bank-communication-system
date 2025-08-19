"""
Test Professional UI Components
Verify all professional UI modules load correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_ui_imports():
    """Test that all UI components import correctly."""
    print("Testing Professional UI Components")
    print("=" * 50)
    
    try:
        # Test professional theme
        print("1. Testing professional theme import...")
        from ui.professional_theme import (
            apply_professional_theme,
            render_professional_header,
            create_metric_card,
            create_status_badge,
            create_professional_card
        )
        print("   ✅ Professional theme loaded successfully")
        
        # Test main app
        print("\n2. Testing main app import...")
        from main import main
        print("   ✅ Main app loaded successfully")
        
        # Test letter scanner
        print("\n3. Testing letter scanner import...")
        from file_handlers.letter_scanner import render_enhanced_letter_management
        print("   ✅ Letter scanner loaded successfully")
        
        # Test cost management
        print("\n4. Testing cost management import...")
        from communication_processing.cost_integration import (
            render_cost_configuration_ui,
            render_cost_analyzer_ui
        )
        print("   ✅ Cost management loaded successfully")
        
        # Test batch processing
        print("\n5. Testing batch processing import...")
        from communication_processing.batch_ui import render_batch_communication_processing
        print("   ✅ Batch processing loaded successfully")
        
        print("\n" + "=" * 50)
        print("✅ ALL PROFESSIONAL UI COMPONENTS LOADED SUCCESSFULLY!")
        print("=" * 50)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nMake sure you've created all the files correctly.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

def test_theme_functions():
    """Test that theme functions work correctly."""
    print("\nTesting Theme Functions")
    print("=" * 50)
    
    try:
        from ui.professional_theme import (
            create_metric_card,
            create_status_badge,
            create_professional_card
        )
        
        # Test metric card
        metric_html = create_metric_card("Test Metric", "1,234", "+5%", "positive")
        assert "metric-container" in metric_html
        print("1. Metric card creation: ✅")
        
        # Test status badge
        badge_html = create_status_badge("Active", "active")
        assert "status-badge" in badge_html
        print("2. Status badge creation: ✅")
        
        # Test professional card
        card_html = create_professional_card("Test Title", "Test subtitle", "Test content")
        assert "pro-card" in card_html
        print("3. Professional card creation: ✅")
        
        print("\n✅ All theme functions working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Theme function test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Professional UI Test Suite")
    print("=" * 50)
    
    # Run tests
    import_success = test_ui_imports()
    
    if import_success:
        theme_success = test_theme_functions()
        
        if theme_success:
            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 50)
            print("\nYour professional UI is ready to run!")
            print("\nTo start the application, run:")
            print("  python -m streamlit run src/main.py")
        else:
            print("\n⚠️ Theme functions need attention")
    else:
        print("\n⚠️ Please fix import errors before proceeding")