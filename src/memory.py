"""
Conversation memory module for AI Architect Bot.
Handles context management, history persistence, and message pruning.
"""

import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from config import Config


class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self, config: Config):
        self.config = config
        self.conversations: List[Dict[str, Any]] = []
        self.current_prompt_type = "architect"  # Default prompt type
        self.logger = logging.getLogger(__name__)
        
        # Token estimation (approximate)
        self.avg_tokens_per_word = 1.3
        self.avg_words_per_message = 15
        
        # Initialize logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup error logging configuration."""
        # Create error log file if it doesn't exist
        if not os.path.exists(self.config.error_log):
            with open(self.config.error_log, 'w') as f:
                f.write(f"Error log initialized at {datetime.now().isoformat()}\n")
        
        # Configure logging to write to error log file
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.error_log),
                logging.StreamHandler()  # Also output to console
            ]
        )
        
    async def load_history(self):
        """Load conversation history from JSON file."""
        try:
            if os.path.exists(self.config.history_file):
                with open(self.config.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', [])
                    
                    # Load metadata
                    metadata = data.get('metadata', {})
                    if metadata:
                        self.logger.info(f"Loaded {len(self.conversations)} messages from history")
            else:
                # Initialize with empty history
                await self.save_history()
                
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            # Initialize with empty history on error
            self.conversations = []
    
    async def save_history(self):
        """Save conversation history to JSON file."""
        try:
            data = {
                'conversations': self.conversations,
                'metadata': {
                    'created_at': self.conversations[0]['timestamp'] if self.conversations else datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_messages': len(self.conversations),
                    'version': '1.0.0'
                }
            }
            
            with open(self.config.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'prompt_type': self.current_prompt_type
        }
        
        self.conversations.append(message)
        
        # Prune old messages if needed
        self._prune_messages()
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get the conversation context for the API."""
        # Calculate approximate token usage
        total_tokens = self._estimate_tokens()
        
        # If we're over the limit, prune messages
        if total_tokens > self.config.max_context_tokens * 0.8:  # Start pruning at 80%
            self._prune_messages()
        
        # Return messages in the format expected by the API
        return [
            {'role': msg['role'], 'content': msg['content']}
            for msg in self.conversations[-self.config.max_history_messages:]
        ]
    
    def get_system_prompt(self) -> str:
        """Get the current system prompt."""
        prompt_file = os.path.join(self.config.prompts_dir, f"{self.current_prompt_type}.txt")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            self.logger.warning(f"Prompt file not found: {prompt_file}")
            # Fall back to architect prompt
            return self._load_default_prompt("architect")
        except Exception as e:
            self.logger.error(f"Error loading prompt: {e}")
            return self._load_default_prompt("architect")
    
    def switch_prompt(self, prompt_type: str) -> bool:
        """Switch to a different system prompt."""
        prompt_file = os.path.join(self.config.prompts_dir, f"{prompt_type}.txt")
        
        if not os.path.exists(prompt_file):
            self.logger.warning(f"Prompt file not found: {prompt_file}")
            return False
        
        self.current_prompt_type = prompt_type
        return True
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversations = []
        # Don't save immediately to avoid I/O on every clear command
    
    def _prune_messages(self):
        """Prune old messages to stay within token limits."""
        # Always keep the last few messages
        min_messages = 5
        
        if len(self.conversations) <= min_messages:
            return
        
        # Calculate tokens from oldest messages
        messages_to_remove = []
        total_tokens = 0
        
        for i, msg in enumerate(self.conversations[:-min_messages]):  # Don't prune the last few messages
            msg_tokens = self._estimate_message_tokens(msg)
            total_tokens += msg_tokens
            
            if total_tokens > self.config.max_context_tokens * 0.3:  # Remove up to 30% of context
                messages_to_remove.append(i)
            else:
                break
        
        # Remove messages from the end to avoid index issues
        for i in reversed(messages_to_remove):
            self.conversations.pop(i)
    
    def _estimate_tokens(self) -> int:
        """Estimate the total number of tokens in the conversation."""
        total_tokens = 0
        for msg in self.conversations:
            total_tokens += self._estimate_message_tokens(msg)
        return total_tokens
    
    def _estimate_message_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate tokens for a single message."""
        # Simple estimation: words * avg_tokens_per_word
        content_words = len(message['content'].split())
        return int(content_words * self.avg_tokens_per_word)
    
    def _load_default_prompt(self, prompt_type: str) -> str:
        """Load a default prompt if the file doesn't exist."""
        default_prompts = {
            'architect': """You are an AI Architect specializing in software design and system architecture. 
Your role is to help users design robust, scalable, and maintainable software systems.

Guidelines:
- Focus on high-level design patterns and architectural decisions
- Consider scalability, performance, and maintainability
- Ask clarifying questions when requirements are unclear
- Provide concrete examples and code snippets when helpful
- Explain trade-offs between different approaches

When in doubt, ask for more context before proceeding.""",
            
            'coder': """You are a Python coding expert with deep knowledge of best practices and modern development techniques.

Guidelines:
- Write clean, readable, and well-documented code
- Follow PEP 8 style guidelines
- Use appropriate data structures and algorithms
- Consider edge cases and error handling
- Explain your code clearly
- Focus on practical, working solutions

When providing code examples:
- Include necessary imports
- Add docstrings for functions and classes
- Use meaningful variable names
- Add comments for complex logic""",
            
            'police_cam': """You are a video analysis expert specializing in analyzing police body camera footage and surveillance video.

Guidelines:
- Focus on objective, factual analysis of visual content
- Describe actions, behaviors, and events without speculation
- Note timestamps and sequence of events
- Identify potential safety concerns or protocol violations
- Maintain professional and objective tone
- Avoid making legal conclusions or judgments

When analyzing video:
- Describe what you observe factually
- Note any concerning behaviors or situations
- Identify potential risks or safety issues
- Suggest appropriate responses based on observed events"""
        }
        
        return default_prompts.get(prompt_type, default_prompts['architect'])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        total_messages = len(self.conversations)
        user_messages = len([m for m in self.conversations if m['role'] == 'user'])
        assistant_messages = len([m for m in self.conversations if m['role'] == 'assistant'])
        
        # Estimate total tokens
        estimated_tokens = self._estimate_tokens()
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'estimated_tokens': estimated_tokens,
            'current_prompt': self.current_prompt_type,
            'token_usage_percentage': f"{(estimated_tokens / self.config.max_context_tokens) * 100:.1f}%"
        }