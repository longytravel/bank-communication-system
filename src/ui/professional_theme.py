"""
Professional Banking UI Theme
Clean, modern, professional design without emojis or clutter.
"""

import streamlit as st

def apply_professional_theme():
    """Apply professional banking theme to the entire application."""
    st.markdown("""
    <style>
    /* Professional Banking Theme - No emojis, clean design */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500&display=swap');
    
    /* Color System - Professional Banking Palette */
    :root {
        --primary-navy: #0F172A;        /* Deep navy for headers */
        --secondary-navy: #1E293B;      /* Lighter navy */
        --accent-blue: #3B82F6;         /* Professional blue */
        --accent-green: #10B981;        /* Success green */
        --text-primary: #0F172A;        /* Dark text */
        --text-secondary: #64748B;      /* Muted text */
        --text-light: #94A3B8;          /* Light text */
        --background: #FFFFFF;          /* Clean white */
        --surface: #F8FAFC;            /* Light gray surface */
        --border: #E2E8F0;             /* Subtle borders */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Global Reset - Clean Professional Look */
    .stApp {
        background: var(--background);
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {display: none;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Professional Header Bar */
    .header-bar {
        background: var(--primary-navy);
        margin: -80px -8rem 2rem -8rem;
        padding: 1.5rem 8rem;
        box-shadow: var(--shadow);
    }
    
    .header-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo {
        width: 40px;
        height: 40px;
        background: var(--accent-blue);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: white;
        font-size: 1.2rem;
    }
    
    .header-title {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .header-subtitle {
        color: var(--text-light);
        font-size: 0.875rem;
        margin: 0;
    }
    
    /* Professional Cards */
    .pro-card {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s;
    }
    
    .pro-card:hover {
        box-shadow: var(--shadow);
    }
    
    .pro-card-header {
        border-bottom: 1px solid var(--border);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .pro-card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .pro-card-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0.25rem 0 0 0;
    }
    
    /* Data Tables - Professional Style */
    .dataframe {
        font-size: 0.875rem !important;
        border: 1px solid var(--border) !important;
    }
    
    .dataframe thead th {
        background: var(--surface) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--border) !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
    }
    
    .dataframe tbody td {
        color: var(--text-primary) !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    /* Metrics - Clean Professional */
    .metric-container {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.25rem;
        height: 100%;
    }
    
    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        font-family: 'Roboto Mono', monospace;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .metric-delta.positive {
        color: var(--accent-green);
    }
    
    .metric-delta.negative {
        color: #EF4444;
    }
    
    /* Status Badges - Professional */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .status-badge.active {
        background: #DCFCE7;
        color: #166534;
    }
    
    .status-badge.pending {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .status-badge.error {
        background: #FEE2E2;
        color: #991B1B;
    }
    
    /* Buttons - Professional Style */
    .stButton > button {
        background: var(--accent-blue);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s;
        box-shadow: var(--shadow-sm);
        text-transform: none;
        letter-spacing: 0;
    }
    
    .stButton > button:hover {
        background: #2563EB;
        box-shadow: var(--shadow);
        transform: translateY(-1px);
    }
    
    /* Primary Button Style */
    div[data-testid="stButton"] button[kind="primary"] {
        background: var(--primary-navy);
    }
    
    /* Secondary Button Style */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: var(--background);
        color: var(--text-primary);
        border: 1px solid var(--border);
    }
    
    /* Navigation Tabs - Professional */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface);
        padding: 0.25rem;
        border-radius: 8px;
        gap: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: 6px;
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--background);
        color: var(--text-primary);
        box-shadow: var(--shadow-sm);
    }
    
    /* Forms - Professional */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 0.875rem;
        color: var(--text-primary);
        background: var(--background);
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Progress Bars - Clean */
    .stProgress > div > div > div {
        background: var(--accent-blue);
    }
    
    .stProgress > div > div {
        background: var(--surface);
    }
    
    /* Alerts - Professional */
    .stAlert {
        border-radius: 6px;
        border: 1px solid;
        font-size: 0.875rem;
    }
    
    /* Charts - Clean Style */
    .plot-container {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Remove all emoji usage */
    .stMarkdown h1::before,
    .stMarkdown h2::before,
    .stMarkdown h3::before,
    .stMarkdown h4::before {
        content: none !important;
    }
    
    /* Professional Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    
    p {
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* Sidebar - Professional */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Data Grid Professional */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Remove streamlit's default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Loading spinner - professional */
    .stSpinner > div {
        border-color: var(--accent-blue) !important;
    }
    
    /* File uploader - professional */
    .stFileUploader {
        border: 2px dashed var(--border);
        border-radius: 8px;
        background: var(--surface);
    }
    
    /* Code blocks - professional */
    .stCodeBlock {
        background: var(--primary-navy) !important;
        border-radius: 6px;
    }
    
    </style>
    """, unsafe_allow_html=True)

def render_professional_header(title: str = "Resonance Bank", subtitle: str = "Communication Intelligence Platform"):
    """Render a professional header without emojis."""
    st.markdown(f"""
    <div class="header-bar">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo">RB</div>
                <div>
                    <h1 class="header-title">{title}</h1>
                    <p class="header-subtitle">{subtitle}</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(label: str, value: str, delta: str = None, delta_type: str = "neutral"):
    """Create a professional metric card without emojis."""
    delta_class = ""
    if delta_type == "positive":
        delta_class = "positive"
    elif delta_type == "negative":
        delta_class = "negative"
    
    delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ''
    
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_badge(text: str, status: str = "active"):
    """Create a professional status badge."""
    return f'<span class="status-badge {status}">{text}</span>'

def create_professional_card(title: str, subtitle: str = None, content: str = None):
    """Create a professional card component."""
    subtitle_html = f'<p class="pro-card-subtitle">{subtitle}</p>' if subtitle else ''
    content_html = f'<div class="pro-card-content">{content}</div>' if content else ''
    
    return f"""
    <div class="pro-card">
        <div class="pro-card-header">
            <h3 class="pro-card-title">{title}</h3>
            {subtitle_html}
        </div>
        {content_html}
    </div>
    """