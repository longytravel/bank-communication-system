"""
Lloyds Banking Group Brand Manager
Provides centralized branding for Streamlit applications
"""

from pathlib import Path
from typing import Dict, Any, Optional

class LloydsBrandManager:
    """Manages Lloyds Banking Group branding across the application."""
    
    def __init__(self):
        """Initialize the brand manager with built-in configuration."""
        # Use built-in configuration - no external JSON needed
        self.config = self._get_default_config()
        self.colors = self.config.get("colors", {})
        self.typography = self.config.get("typography", {})
        self.spacing = self.config.get("spacing", {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default Lloyds brand configuration."""
        return {
            "colors": {
                "primary": {
                    "lloyds_green": "#006A4D",
                    "lloyds_green_dark": "#00523B",
                    "lloyds_green_light": "#4D9B84"
                },
                "secondary": {
                    "heritage_green": "#024731",
                    "bright_green": "#00B67A",
                    "mint_green": "#E8F4F0"
                },
                "neutral": {
                    "black": "#000000",
                    "charcoal": "#2D2D2D",
                    "grey_dark": "#666666",
                    "grey_medium": "#999999",
                    "grey_light": "#CCCCCC",
                    "grey_pale": "#F5F5F5",
                    "white": "#FFFFFF"
                },
                "functional": {
                    "error": "#D32F2F",
                    "warning": "#F57C00",
                    "success": "#388E3C",
                    "info": "#1976D2"
                }
            },
            "typography": {
                "fontFamilies": {
                    "primary": "Arial, Helvetica, sans-serif",
                    "secondary": "Georgia, serif",
                    "monospace": "Consolas, Monaco, monospace"
                }
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
                "2xl": "48px",
                "3xl": "64px"
            }
        }
    
    def get_color(self, category: str, name: str) -> str:
        """Get a specific color from the brand palette."""
        return self.colors.get(category, {}).get(name, "#000000")
    
    def get_primary_color(self) -> str:
        """Get the primary brand color."""
        return self.get_color("primary", "lloyds_green")
    
    def get_custom_css(self) -> str:
        """Generate custom CSS for Streamlit components."""
        primary = self.get_color("primary", "lloyds_green")
        primary_dark = self.get_color("primary", "lloyds_green_dark")
        mint = self.get_color("secondary", "mint_green")
        
        return f"""
        <style>
        /* Lloyds Banking Group Custom Styling */
        
        /* Main header styling */
        .main-header {{
            background: linear-gradient(135deg, {primary} 0%, {primary_dark} 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        
        /* Professional card styling */
        .professional-card {{
            background: white;
            border-left: 4px solid {primary};
            padding: 1.5rem;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        
        /* Success message styling */
        .success-message {{
            background: {mint};
            color: {primary_dark};
            padding: 1rem;
            border-radius: 4px;
            border-left: 4px solid {primary};
        }}
        
        /* Button overrides */
        .stButton > button {{
            background-color: {primary};
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {primary_dark};
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        /* Metric cards */
        div[data-testid="metric-container"] {{
            background-color: {mint};
            border-left: 3px solid {primary};
            padding: 1rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: white;
            border-color: {primary};
            color: {primary};
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {primary};
            color: white;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: {mint};
            color: {primary_dark};
            border-radius: 4px;
        }}
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: #F5F5F5;
            border-right: 2px solid {primary};
        }}
        
        /* Success/Info/Warning alerts */
        .stAlert {{
            border-left: 4px solid {primary};
        }}
        
        /* Select boxes */
        .stSelectbox > div > div {{
            border-color: {primary};
        }}
        
        /* Text input fields */
        .stTextInput > div > div > input {{
            border-color: {primary};
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {primary_dark};
            box-shadow: 0 0 0 1px {primary_dark};
        }}
        </style>
        """
    
    def create_header(self, title: str, subtitle: str = "") -> str:
        """Create a branded header component."""
        header_html = f"""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">{title}</h1>
            {"<p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """
        return header_html
    
    def create_metric_card(self, label: str, value: str, delta: str = "") -> str:
        """Create a branded metric card."""
        primary = self.get_color("primary", "lloyds_green")
        
        return f"""
        <div style="background: #E8F4F0; border-left: 3px solid {primary}; 
                    padding: 1rem; border-radius: 4px; margin: 0.5rem 0;">
            <div style="color: #666; font-size: 0.875rem; margin-bottom: 0.25rem;">{label}</div>
            <div style="color: {primary}; font-size: 1.5rem; font-weight: 700;">{value}</div>
            {"<div style='color: #00B67A; font-size: 0.875rem; margin-top: 0.25rem;'>↑ " + delta + "</div>" if delta else ""}
        </div>
        """
    
    def apply_theme(self):
        """Apply the Lloyds theme to the current Streamlit page."""
        import streamlit as st
        
        # Inject custom CSS
        st.markdown(self.get_custom_css(), unsafe_allow_html=True)
        
        # Note: set_page_config must be called by the main app, not here

# Singleton instance for easy import
brand_manager = LloydsBrandManager()

# Convenience functions for direct import
def apply_lloyds_theme():
    """Apply Lloyds Banking Group theme to the Streamlit app."""
    brand_manager.apply_theme()

def get_lloyds_header(title: str, subtitle: str = "") -> str:
    """Get a Lloyds-branded header."""
    return brand_manager.create_header(title, subtitle)

def get_lloyds_css() -> str:
    """Get Lloyds custom CSS."""
    return brand_manager.get_custom_css()