"""
API Integration Module
Handles all external API calls (Claude, OpenAI, etc.)
"""

from .claude_api import ClaudeAPI
from .openai_api import OpenAIAPI
from .api_manager import APIManager

__all__ = [
    'ClaudeAPI',
    'OpenAIAPI', 
    'APIManager'
] 
