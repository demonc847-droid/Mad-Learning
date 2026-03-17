"""
Configuration module for AI Architect Bot Phase 1.
Handles environment variables, API configuration, and model definitions.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class that loads settings from environment variables."""
    
    def __init__(self):
        # API Configuration
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        # Bot Configuration
        self.bot_name = os.getenv('BOT_NAME', 'AI_Architect_Bot')
        self.max_context_tokens = int(os.getenv('MAX_CONTEXT_TOKENS', '8192'))
        self.max_history_messages = int(os.getenv('MAX_HISTORY_MESSAGES', '50'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.top_p = float(os.getenv('TOP_P', '0.9'))
        
        # API Configuration
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'HTTP-Referer': 'http://localhost',
            'X-Title': 'AI Architect Bot',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # Model Selection from Environment Variables
        self.primary_model = os.getenv('PRIMARY_MODEL', 'openai/gpt-4o-mini')
        fallback_models_str = os.getenv('FALLBACK_MODELS', 'anthropic/claude-sonnet-4.6,google/gemini-3.1-pro-preview,qwen/qwen3.5-35b-a3b')
        self.fallback_models: List[str] = [model.strip() for model in fallback_models_str.split(',')]
        
        # Free Models for Failover Rotation Strategy (used by ModelEngine)
        self.free_models: List[str] = [
            'openai/gpt-4o-mini',
            'anthropic/claude-sonnet-4.6', 
            'google/gemini-3.1-pro-preview',
            'qwen/qwen3.5-35b-a3b'
        ]
        
        # File Paths
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.history_file = os.path.join(self.data_dir, 'history.json')
        self.error_log = os.path.join(self.data_dir, 'error.log')
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.prompts_dir, exist_ok=True)
    
    @property
    def available_models(self) -> List[str]:
        """Get list of all available models (primary + fallback)."""
        models = [self.primary_model] if hasattr(self, 'primary_model') else []
        models.extend(self.fallback_models if hasattr(self, 'fallback_models') else [])
        return list(dict.fromkeys(models))  # Remove duplicates while preserving order
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get model-specific configuration."""
        # Model-specific token limits and settings
        model_limits = {
            'openai/gpt-4o-mini': {'max_tokens': 128000, 'supports_system': True},
            'anthropic/claude-sonnet-4.6': {'max_tokens': 200000, 'supports_system': True},
            'google/gemini-3.1-pro-preview': {'max_tokens': 32768, 'supports_system': True},
            'qwen/qwen3.5-35b-a3b': {'max_tokens': 32768, 'supports_system': True},
        }
        
        return model_limits.get(model_name, {'max_tokens': 32768, 'supports_system': True})
    
    def validate(self):
        """Validate configuration settings."""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        if self.max_context_tokens <= 0:
            raise ValueError("MAX_CONTEXT_TOKENS must be positive")
        
        if not 0 <= self.temperature <= 1:
            raise ValueError("TEMPERATURE must be between 0 and 1")
        
        if not 0 <= self.top_p <= 1:
            raise ValueError("TOP_P must be between 0 and 1")


# Global configuration instance
config = Config()