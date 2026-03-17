"""
Model Management Module for AI Architect Bot Phase 2.
Implements the Rotation Engine with failover strategy and smart model management.
"""

import time
import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

from config import Config


class ModelEngine:
    """
    Model Engine for managing model rotation and failover strategy.
    
    Features:
    - Model status tracking (Available, Busy, Rate-Limited)
    - Failover rotation on errors
    - Smart cooldown timers for rate-limited models
    - Timeout handling for Karachi internet optimization
    """
    
    class ModelStatus:
        """Enum-like class for model status states."""
        AVAILABLE = "Available"
        BUSY = "Busy"
        RATE_LIMITED = "Rate-Limited"
    
    def __init__(self, config: Config):
        """
        Initialize the Model Engine.
        
        Args:
            config (Config): Configuration object containing free models list
        """
        self.config = config
        # Use working models from Phase 1 instead of free models for testing
        self.free_models: List[str] = [
            'openai/gpt-4o-mini',
            'anthropic/claude-sonnet-4.6', 
            'google/gemini-3.1-pro-preview',
            'qwen/qwen3.5-35b-a3b'
        ]
        self.current_model_index: int = 0
        
        # Model status tracking
        self.model_status: Dict[str, str] = {}
        self.rate_limit_cooldowns: Dict[str, datetime] = {}
        
        # Initialize all models as available
        for model in self.free_models:
            self.model_status[model] = self.ModelStatus.AVAILABLE
    
    def _is_model_available(self, model: str) -> bool:
        """
        Check if a model is available (not rate-limited or in cooldown).
        
        Args:
            model (str): Model identifier
            
        Returns:
            bool: True if model is available
        """
        if self.model_status[model] == self.ModelStatus.RATE_LIMITED:
            # Check if cooldown period has expired
            if model in self.rate_limit_cooldowns:
                cooldown_end = self.rate_limit_cooldowns[model]
                if datetime.now() < cooldown_end:
                    return False
                else:
                    # Cooldown expired, reset status
                    self.model_status[model] = self.ModelStatus.AVAILABLE
                    del self.rate_limit_cooldowns[model]
        
        return self.model_status[model] == self.ModelStatus.AVAILABLE
    
    def _get_next_available_model(self) -> Optional[str]:
        """
        Get the next available model in the rotation.
        
        Returns:
            Optional[str]: Next available model or None if all are unavailable
        """
        # Check if all models are currently rate-limited with active cooldowns
        all_rate_limited_with_cooldown = True
        for model in self.free_models:
            if self.model_status[model] != self.ModelStatus.RATE_LIMITED or model not in self.rate_limit_cooldowns:
                all_rate_limited_with_cooldown = False
                break
        
        # If all models are rate-limited with active cooldowns, return None immediately
        if all_rate_limited_with_cooldown:
            return None
        
        # Try all models starting from current index
        for _ in range(len(self.free_models)):
            model = self.free_models[self.current_model_index]
            
            if self._is_model_available(model):
                return model
            
            # Move to next model
            self.current_model_index = (self.current_model_index + 1) % len(self.free_models)
        
        return None
    
    def _handle_rate_limit(self, model: str) -> None:
        """
        Handle rate limit by setting cooldown timer.
        
        Args:
            model (str): Model that hit rate limit
        """
        self.model_status[model] = self.ModelStatus.RATE_LIMITED
        # Set 60-second cooldown
        self.rate_limit_cooldowns[model] = datetime.now() + timedelta(seconds=60)
    
    def _make_api_request(self, model: str, prompt: str, context: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[bool, str]:
        """
        Make a single API request to a specific model.
        
        Args:
            model (str): Target model
            prompt (str): User prompt
            context (List[Dict[str, str]]): Conversation context
            system_prompt (Optional[str]): System prompt to include in the request
            
        Returns:
            Tuple[bool, str]: (success, response_or_error_message)
        """
        try:
            # Prepare the messages list
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation context
            messages.extend(context)
            
            # Add current user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": 1000,  # Reasonable limit for testing
                "stream": False
            }
            
            # Make the API request with timeout for Karachi optimization
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=self.config.headers,
                json=payload,
                timeout=15  # 15-second timeout for Karachi internet
            )
            
            # Handle different HTTP status codes using match/case (Python 3.12+)
            match response.status_code:
                case 200:
                    # Success
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return True, data["choices"][0]["message"]["content"]
                    else:
                        return False, "No response generated"
                
                case 429:
                    # Rate limited
                    self._handle_rate_limit(model)
                    return False, f"Rate limit exceeded for {model}"
                
                case 401:
                    # Unauthorized
                    return False, "Authentication failed - check API key"
                
                case 400:
                    # Bad request
                    return False, "Bad request - invalid parameters"
                
                case 500 | 502 | 503 | 504:
                    # Server errors
                    return False, f"Server error {response.status_code}"
                
                case _:
                    # Other errors
                    return False, f"HTTP {response.status_code}: {response.text}"
            
        except requests.exceptions.Timeout:
            # Timeout handling for Karachi internet optimization
            return False, f"Request timeout for {model}"
        
        except requests.exceptions.ConnectionError:
            return False, f"Connection error for {model}"
        
        except requests.exceptions.RequestException as e:
            return False, f"Request error for {model}: {str(e)}"
    
    def get_completion(self, prompt: str, context: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Get completion from the best available model with failover strategy.
        
        Args:
            prompt (str): User prompt
            context (List[Dict[str, str]]): Conversation context
            system_prompt (Optional[str]): System prompt to include in the request
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (response_text, model_name) or (None, None) if all fail
        """
        max_retries = len(self.free_models)  # Try each model at most once
        attempts = 0
        
        while attempts < max_retries:
            # Get next available model
            model = self._get_next_available_model()
            
            if model is None:
                # All models are currently unavailable
                return None, None
            
            # Mark model as busy
            self.model_status[model] = self.ModelStatus.BUSY
            
            try:
                # Make API request with system prompt
                success, result = self._make_api_request(model, prompt, context, system_prompt)
                
                if success:
                    # Success! Mark as available and return
                    self.model_status[model] = self.ModelStatus.AVAILABLE
                    return result, model
                else:
                    # Request failed, mark as available for next attempt
                    self.model_status[model] = self.ModelStatus.AVAILABLE
                    
                    # If it was a timeout, just try next model
                    if "timeout" in result.lower():
                        pass  # Continue to next model
                    # If it was rate limited, _make_api_request already handled it
                    elif "rate limit" in result.lower():
                        pass  # Continue to next model
                    else:
                        # Other errors, just continue
                        pass
                        
            except Exception as e:
                # Unexpected error, mark as available and continue
                self.model_status[model] = self.ModelStatus.AVAILABLE
            
            # Move to next model for next iteration
            self.current_model_index = (self.current_model_index + 1) % len(self.free_models)
            attempts += 1
        
        # All models failed
        return None, None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of model statuses for display.
        
        Returns:
            Dict[str, Any]: Status information
        """
        available_models = [m for m in self.free_models if self._is_model_available(m)]
        busy_models = [m for m in self.free_models if self.model_status[m] == self.ModelStatus.BUSY]
        rate_limited_models = [m for m in self.free_models if self.model_status[m] == self.ModelStatus.RATE_LIMITED]
        
        return {
            "total_models": len(self.free_models),
            "available_models": available_models,
            "busy_models": busy_models,
            "rate_limited_models": rate_limited_models,
            "current_model_index": self.current_model_index,
            "current_model": self.free_models[self.current_model_index] if self.free_models else None
        }