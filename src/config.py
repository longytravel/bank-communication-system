"""
Configuration Module for Bank Communication System
Handles API keys, file paths, and system settings securely.
"""

import os
from pathlib import Path
from typing import Optional
import logging
from dotenv import load_dotenv

class Config:
    """Central configuration management for the bank communication system."""
    
    def __init__(self):
        """Initialize configuration with secure defaults."""
        load_dotenv()  # Load .env file
        self.setup_logging()
        self.base_dir = self._get_base_directory()
        self._setup_directories()
        self._load_api_keys()
    
    def _get_base_directory(self) -> Path:
        """Get the base directory for the project."""
        # Get the directory where this config.py file is located
        current_file = Path(__file__).resolve()
        # Go up two levels: from src/config.py to project root
        return current_file.parent.parent
    
    def _setup_directories(self):
        """Set up all required directories."""
        self.directories = {
            'data': self.base_dir / 'data',
            'customer_profiles': self.base_dir / 'data' / 'customer_profiles',
            'letters': self.base_dir / 'data' / 'letters', 
            'outputs': self.base_dir / 'data' / 'outputs',
            'voice_notes': self.base_dir / 'data' / 'voice_notes',
            'logs': self.base_dir / 'logs'
        }
        
        # Create directories if they don't exist
        for dir_name, dir_path in self.directories.items():
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Directory ready: {dir_name} -> {dir_path}")
    
    def _load_api_keys(self):
        """Load API keys from environment variables."""
        self.api_keys = {
            'claude': os.getenv('CLAUDE_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'did': os.getenv('DID_API_KEY')
        }
        
        # Check for missing API keys
        missing_keys = [key for key, value in self.api_keys.items() if not value]
        if missing_keys:
            logging.warning(f"Missing API keys: {missing_keys}")
            logging.info("Set them in your .env file or environment variables")
    
    def setup_logging(self):
        """Set up logging configuration."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'app.log'),
                logging.StreamHandler()  # Also log to console
            ]
        )
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        key = self.api_keys.get(service.lower())
        if not key:
            logging.error(f"API key for {service} not found!")
        return key
    
    def get_directory(self, name: str) -> Path:
        """Get path for a specific directory."""
        if name not in self.directories:
            raise ValueError(f"Unknown directory: {name}")
        return self.directories[name]
    
    def is_configured(self) -> bool:
        """Check if the system is properly configured."""
        required_keys = ['claude', 'openai'] 
        missing = [key for key in required_keys if not self.api_keys.get(key)]
        
        if missing:
            logging.error(f"Configuration incomplete. Missing API keys: {missing}")
            return False
        
        logging.info("✅ System fully configured!")
        return True

# Global configuration instance
config = Config()

# Convenience functions for easy access
def get_api_key(service: str) -> Optional[str]:
    """Get API key for a service."""
    return config.get_api_key(service)

def get_directory(name: str) -> Path:
    """Get directory path."""
    return config.get_directory(name)

def is_configured() -> bool:
    """Check if system is ready."""
    return config.is_configured()