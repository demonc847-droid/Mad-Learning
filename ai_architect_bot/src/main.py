#!/usr/bin/env python3
"""
AI Architect Bot - Phase 4 Implementation
Interactive chat with enhanced UI, visual feedback, and professional interface.
"""

import sys
import signal
import asyncio
import uuid
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns

from config import Config
from models import ModelEngine
from memory import ConversationMemory
from utils import (
    check_connection, check_env_file, setup_logging, log_error,
    create_thinking_spinner, export_chat_history, show_model_stats,
    clear_screen, create_status_bar, format_welcome_with_status
)


class AIArchitectBot:
    """Enhanced AI Architect Bot with Phase 4 UI improvements."""
    
    def __init__(self):
        self.console = Console()
        self.config = None
        self.engine = None
        self.memory = None
        self.session_id = str(uuid.uuid4())
        self.running = True
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            self.console.print("\n[bold yellow]Goodbye![/bold yellow]")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
    
    async def initialize(self):
        """Initialize all bot components."""
        # Clear screen for professional appearance
        clear_screen()
        
        # System Boot Sequence
        self.console.print("\n")
        self.console.print(Panel(
            "[bold cyan]AI Architect Bot - Phase 4[/bold cyan]\n[bold]Enhanced UI & Professional Interface[/bold]\nRich Live • Status Bar • Export • Reliability",
            title="System Boot",
            border_style="blue",
            padding=(1, 2)
        ))
        
        # Environment Check
        self.console.print("\n[bold]1. Environment Check:[/bold]")
        with self.console.status("[bold green]Checking environment configuration...[/bold green]", spinner="dots"):
            env_ok = check_env_file()
        
        if env_ok:
            self.console.print("   ✓ .env file found and configured")
        else:
            self.console.print("   ✗ .env file missing or API key not configured")
            self.console.print("   [yellow]Please copy .env.template to .env and add your OpenRouter API key[/yellow]")
            return False
        
        # Connection Test
        self.console.print("\n[bold]2. API Connectivity:[/bold]")
        with self.console.status("[bold green]Testing OpenRouter connection...[/bold green]", spinner="dots"):
            connection_ok = check_connection()
        
        if connection_ok:
            self.console.print("   ✓ OpenRouter API connection successful")
        else:
            self.console.print("   ✗ OpenRouter API connection failed")
            self.console.print("   [yellow]Please check:[/yellow]")
            self.console.print("   [yellow]  • Your internet connection is working[/yellow]")
            self.console.print("   [yellow]  • Your OpenRouter API key is valid[/yellow]")
            self.console.print("   [yellow]  • Try again in a moment (server may be busy)[/yellow]")
            return False
        
        # Configuration Load
        self.console.print("\n[bold]3. Configuration Load:[/bold]")
        try:
            self.config = Config()
            self.console.print(f"   ✓ Bot Name: {self.config.bot_name}")
            self.console.print(f"   ✓ Base URL: {self.config.base_url}")
            self.console.print(f"   ✓ HTTP-Referer: {self.config.headers['HTTP-Referer']}")
            self.console.print(f"   ✓ X-Title: {self.config.headers['X-Title']}")
        except Exception as e:
            self.console.print(f"   ✗ Configuration error: {e}")
            return False
        
        # Initialize Components
        self.console.print("\n[bold]4. Component Initialization:[/bold]")
        try:
            # Initialize Model Engine
            self.engine = ModelEngine(self.config)
            self.console.print(f"   ✓ Model Engine initialized with {len(self.engine.free_models)} free models")
            self.console.print(f"   ✓ Failover rotation strategy: ENABLED")
            self.console.print(f"   ✓ Karachi internet optimization: ENABLED")
            
            # Initialize Memory System
            self.memory = ConversationMemory(self.config)
            await self.memory.load_history()
            self.console.print(f"   ✓ Memory system initialized")
            self.console.print(f"   ✓ Conversation history loaded: {len(self.memory.conversations)} messages")
            
            # Setup logging
            setup_logging()
            self.console.print(f"   ✓ Error logging configured")
            
        except Exception as e:
            self.console.print(f"   ✗ Initialization error: {e}")
            log_error("Component initialization failed", str(e))
            return False
        
        # Show welcome message with session info
        self.console.print("\n")
        self.console.print(format_welcome_with_status(self.config.bot_name, self.session_id))
        
        return True
    
    def display_status_bar(self):
        """Display the persistent status bar."""
        status_text = create_status_bar(self.engine, self.memory, self.session_id)
        self.console.print(f"[bold blue]{status_text}[/bold blue]")
    
    def format_bot_response(self, response: str, model_name: str) -> Panel:
        """Format the bot's response with model information."""
        from rich.markdown import Markdown
        
        # Create markdown from response for proper code highlighting
        markdown = Markdown(response)
        
        # Add model info
        footer = Text()
        footer.append("Model: ", style="dim")
        footer.append(f"{model_name}", style="bold green")
        
        return Panel(
            markdown,
            title="🤖 AI Architect Bot",
            subtitle=footer,
            border_style="cyan",
            padding=(1, 2)
        )
    
    def show_help(self):
        """Display help information."""
        help_text = """
# Available Commands

**/help** - Show this help message
**/clear** - Clear conversation history
**/models** - Show model status and health
**/prompt [type]** - Switch system prompt (architect, coder, police_cam)
**/status** - Show bot status and statistics
**/export** - Export chat history to text file
**/stats** - Show model health statistics
**/exit** - Exit the bot

# System Prompts

- **architect** - General software architecture and design
- **coder** - Python coding and development assistance  
- **police_cam** - Video analysis and description

# Tips

- The bot automatically manages conversation context
- Models are rotated based on availability and performance
- Conversation history is saved automatically
- Use /clear if you want to start fresh
"""
        
        self.console.print(Panel(
            help_text,
            title="Help",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def show_status(self):
        """Show comprehensive bot status."""
        stats = self.memory.get_statistics()
        
        # Create status table
        table = Table(title="Bot Status", show_header=False, box=None)
        table.add_row("Bot Name:", f"[bold]{self.config.bot_name}[/bold]")
        table.add_row("Session ID:", f"[bold]{self.session_id[:8]}...[/bold]")
        table.add_row("Current Model:", f"[bold]{self.engine.get_status_summary()['current_model']}[/bold]")
        table.add_row("Current Prompt:", f"[bold]{stats['current_prompt']}[/bold]")
        table.add_row("Total Messages:", f"[bold]{stats['total_messages']}[/bold]")
        table.add_row("User Messages:", f"[bold]{stats['user_messages']}[/bold]")
        table.add_row("Assistant Messages:", f"[bold]{stats['assistant_messages']}[/bold]")
        table.add_row("Token Usage:", f"[bold]{stats['token_usage_percentage']}[/bold]")
        table.add_row("Estimated Tokens:", f"[bold]{stats['estimated_tokens']}[/bold]")
        
        self.console.print(table)
    
    async def handle_command(self, command: str):
        """Handle user commands."""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == '/help':
            self.show_help()
        
        elif cmd == '/clear':
            self.console.print("[bold yellow]Clearing conversation history...[/bold yellow]")
            self.memory.clear_history()
            await self.memory.save_history()
            self.console.print("[bold green]Conversation history cleared![/bold green]")
        
        elif cmd == '/models':
            self.display_model_status()
        
        elif cmd == '/status':
            self.show_status()
        
        elif cmd == '/prompt':
            if len(parts) < 2:
                self.console.print("[red]Usage: /prompt [type][/red]")
                self.console.print("[yellow]Available types: architect, coder, police_cam[/yellow]")
            else:
                prompt_type = parts[1].lower()
                if self.memory.switch_prompt(prompt_type):
                    self.console.print(f"[bold green]Switched to '{prompt_type}' prompt[/bold green]")
                else:
                    self.console.print(f"[red]Failed to load '{prompt_type}' prompt[/red]")
        
        elif cmd == '/export':
            success = export_chat_history(self.memory, self.console)
            if success:
                self.console.print("[bold green]Chat history exported successfully![/bold green]")
        
        elif cmd == '/stats':
            show_model_stats(self.engine, self.console)
        
        elif cmd in ['/quit', '/exit', '/bye']:
            self.running = False
            self.console.print("[bold yellow]Goodbye![/bold yellow]")
        
        else:
            self.console.print(f"[bold red]Unknown command: {cmd}[/bold red]")
            self.console.print("Use /help for available commands.")
    
    def display_model_status(self):
        """Display current model status in a formatted panel."""
        status = self.engine.get_status_summary()
        
        # Create status text
        status_text = Text()
        status_text.append("Current Model: ", style="bold")
        status_text.append(f"{status['current_model']}\n", style="cyan bold")
        
        status_text.append("Available: ", style="bold")
        status_text.append(f"{len(status['available_models'])}/{status['total_models']}\n", style="green")
        
        if status['busy_models']:
            status_text.append("Busy: ", style="bold")
            status_text.append(f"{', '.join(status['busy_models'])}\n", style="yellow")
        
        if status['rate_limited_models']:
            status_text.append("Rate Limited: ", style="bold")
            status_text.append(f"{', '.join(status['rate_limited_models'])}\n", style="red")
        
        self.console.print(Panel(
            status_text,
            title="🤖 Model Engine Status",
            border_style="blue",
            padding=(1, 2)
        ))
    
    async def run(self):
        """Main interaction loop with enhanced UI and reliability."""
        try:
            # Initialize components
            if not await self.initialize():
                return
            
            # Main interaction loop with try/finally for reliability
            while self.running:
                try:
                    # Display status bar
                    self.display_status_bar()
                    
                    # Get user input
                    user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                    
                    # Handle commands
                    if user_input.startswith('/'):
                        await self.handle_command(user_input)
                        continue
                    
                    # Add user message to memory
                    self.memory.add_message("user", user_input)
                    
                    # Get system prompt
                    system_prompt = self.memory.get_system_prompt()
                    
                    # Get conversation context
                    context = self.memory.get_context()
                    
                    # Get response from Model Engine with enhanced visual feedback
                    self.console.print(f"\n[bold]Requesting response...[/bold]")
                    
                    # Use Rich Live for enhanced visual feedback
                    with create_thinking_spinner() as progress:
                        progress.add_task("Processing with failover rotation...", total=None)
                        response, model_used = self.engine.get_completion(user_input, context, system_prompt)
                    
                    if response and model_used:
                        # Add assistant response to memory
                        self.memory.add_message("assistant", response)
                        
                        # Save history periodically
                        await self.memory.save_history()
                        
                        # Display response with model information
                        self.console.print(self.format_bot_response(response, model_used))
                        self.console.print(f"[bold green]✓ Response from: {model_used}[/bold green]")
                        self.console.print(f"[bold blue]Prompt: {self.memory.current_prompt_type}[/bold blue]")
                    else:
                        self.console.print("[bold red]✗ All models failed or unavailable[/bold red]")
                        self.console.print("[yellow]Try again in a moment or check your internet connection[/yellow]")
                        log_error("All models failed to respond")
                    
                    self.console.print("\n" + "="*80 + "\n")
                    
                except KeyboardInterrupt:
                    self.running = False
                    self.console.print("\n[bold yellow]Goodbye![/bold yellow]")
                
                except Exception as e:
                    self.console.print(f"[bold red]Error: {e}[/bold red]")
                    log_error("Unexpected error in main loop", str(e))
        
        except Exception as e:
            log_error("Critical error in bot execution", str(e))
        
        finally:
            # Ensure history is saved even on exit
            try:
                if self.memory:
                    await self.memory.save_history()
                    self.console.print("[bold blue]Session history saved successfully.[/bold blue]")
            except Exception as e:
                log_error("Failed to save history on exit", str(e))


async def main():
    """Main entry point for Phase 4 - Enhanced AI Architect Bot."""
    bot = AIArchitectBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())