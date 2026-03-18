"""
Utility functions for AI Architect Bot Phase 1.
Provides formatting, logging, command handling, and connectivity utilities.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from config import Config


def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(os.getenv('ERROR_LOG', 'data/error.log'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(os.getenv('ERROR_LOG', 'data/error.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def log_error(message: str, error_details: Optional[str] = None):
    """
    Simple error logging function for Phase 3.
    
    Args:
        message (str): Error message to log
        error_details (Optional[str]): Additional error details
    """
    logger = logging.getLogger(__name__)
    
    if error_details:
        logger.error(f"{message} - Details: {error_details}")
    else:
        logger.error(message)


def check_connection() -> bool:
    """
    Check connectivity to OpenRouter API with timeout for slow internet.
    
    Returns:
        bool: True if connection successful, False otherwise.
    """
    import requests
    
    try:
        config = Config()
        response = requests.get(
            f"{config.base_url}/models",
            headers=config.headers,
            timeout=30  # Increased timeout to 30 seconds for better reliability
        )
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("Connection check failed: Request timed out (30s)")
        return False
    except requests.exceptions.ConnectionError:
        print("Connection check failed: Network connection error")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Connection check failed: {e}")
        return False
    except Exception as e:
        print(f"Connection check failed: Unexpected error - {e}")
        return False


def check_env_file() -> bool:
    """
    Verify if .env file exists and API key is not empty.
    
    Returns:
        bool: True if .env file exists and has API key, False otherwise.
    """
    if not os.path.exists('.env'):
        return False
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
            # Check if OPENROUTER_API_KEY is present and not empty
            for line in content.split('\n'):
                if line.startswith('OPENROUTER_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    return bool(api_key and api_key != 'your_openrouter_api_key_here')
        return False
    except Exception:
        return False


def format_welcome_message(bot_name: str, model: str) -> Panel:
    """Format the welcome message panel."""
    welcome_text = Text()
    welcome_text.append("🤖 ", style="bold yellow")
    welcome_text.append(f"{bot_name}", style="bold cyan")
    welcome_text.append(" is ready!\n\n", style="bold")
    welcome_text.append("Current Model: ", style="dim")
    welcome_text.append(f"{model}", style="bold green")
    welcome_text.append("\n\nType '/help' for available commands.")
    
    return Panel(
        welcome_text,
        title="Welcome",
        border_style="blue",
        padding=(1, 2)
    )


def format_bot_response(response: str, model: str) -> Panel:
    """Format the bot's response."""
    # Create markdown from response
    markdown = Markdown(response)
    
    # Add model info
    footer = Text()
    footer.append("Model: ", style="dim")
    footer.append(f"{model}", style="bold green")
    
    return Panel(
        markdown,
        title="🤖 AI Architect Bot",
        subtitle=footer,
        border_style="cyan",
        padding=(1, 2)
    )


def format_error_message(error: str) -> Panel:
    """Format error messages."""
    error_text = Text()
    error_text.append("❌ Error: ", style="bold red")
    error_text.append(error, style="red")
    
    return Panel(
        error_text,
        title="Error",
        border_style="red",
        padding=(1, 2)
    )


def show_model_status(model_manager: Any, console: Console):
    """Display model status in a formatted table."""
    console.print("\n")
    return model_manager.show_model_status()


async def handle_command(command: str, bot: Any):
    """Handle user commands."""
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == '/help':
        show_help(bot.console)
    
    elif cmd == '/clear':
        await handle_clear_command(bot)
    
    elif cmd == '/models':
        await show_model_status(bot.model_manager, bot.console)
    
    elif cmd == '/prompt':
        await handle_prompt_command(parts, bot)
    
    elif cmd == '/status':
        await handle_status_command(bot)
    
    elif cmd == '/exit':
        bot.running = False
        bot.console.print("[bold yellow]Goodbye![/bold yellow]")
    
    else:
        bot.console.print(format_error_message(f"Unknown command: {cmd}"))


def show_help(console: Console):
    """Display help information."""
    help_text = """
# Available Commands

**/help** - Show this help message
**/clear** - Clear conversation history
**/models** - Show model status and health
**/prompt [type]** - Switch system prompt (architect, coder, police_cam)
**/status** - Show bot status and statistics
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
    
    console.print(Panel(
        Markdown(help_text),
        title="Help",
        border_style="blue",
        padding=(1, 2)
    ))


async def handle_clear_command(bot: Any):
    """Handle the /clear command."""
    bot.console.print("[bold yellow]Clearing conversation history...[/bold yellow]")
    bot.memory.clear_history()
    await bot.memory.save_history()
    bot.console.print("[bold green]Conversation history cleared![/bold green]")


async def handle_prompt_command(parts: List[str], bot: Any):
    """Handle the /prompt command."""
    if len(parts) < 2:
        bot.console.print(format_error_message("Usage: /prompt [type]"))
        return
    
    prompt_type = parts[1].lower()
    available_prompts = ['architect', 'coder', 'police_cam']
    
    if prompt_type not in available_prompts:
        bot.console.print(format_error_message(f"Available prompts: {', '.join(available_prompts)}"))
        return
    
    if bot.memory.switch_prompt(prompt_type):
        bot.console.print(f"[bold green]Switched to '{prompt_type}' prompt[/bold green]")
    else:
        bot.console.print(format_error_message(f"Failed to load '{prompt_type}' prompt"))


async def handle_status_command(bot: Any):
    """Handle the /status command."""
    stats = bot.memory.get_statistics()
    
    # Create status table
    table = Table(title="Bot Status", show_header=False, box=None)
    table.add_row("Bot Name:", f"[bold]{bot.config.bot_name}[/bold]")
    table.add_row("Current Model:", f"[bold]{bot.current_model}[/bold]")
    table.add_row("Current Prompt:", f"[bold]{stats['current_prompt']}[/bold]")
    table.add_row("Total Messages:", f"[bold]{stats['total_messages']}[/bold]")
    table.add_row("User Messages:", f"[bold]{stats['user_messages']}[/bold]")
    table.add_row("Assistant Messages:", f"[bold]{stats['assistant_messages']}[/bold]")
    table.add_row("Token Usage:", f"[bold]{stats['token_usage_percentage']}[/bold]")
    table.add_row("Estimated Tokens:", f"[bold]{stats['estimated_tokens']}[/bold]")
    
    bot.console.print(table)
    
    # Show model status
    await show_model_status(bot.model_manager, bot.console)


def format_timestamp() -> str:
    """Get current timestamp in a readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_input(prompt: str, console: Console, required: bool = True) -> Optional[str]:
    """Get user input with validation."""
    while True:
        value = Prompt.ask(f"[bold]{prompt}[/bold]")
        if not value.strip() and required:
            console.print("[red]This field is required.[/red]")
            continue
        return value.strip() if value else None


def format_size(bytes_size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def create_progress_bar(description: str = "Processing...") -> Any:
    """Create a progress bar for long operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True
    )


def create_thinking_spinner() -> Any:
    """Create a thinking spinner for API calls."""
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold green]Thinking...[/bold green]"),
        transient=True
    )


def format_export_filename() -> str:
    """Generate a timestamped filename for chat exports."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"chat_export_{timestamp}.txt"


def export_chat_history(memory: Any, console: Console) -> bool:
    """
    Export chat history to a readable text file.
    
    Args:
        memory: Memory object containing conversation history
        console: Rich console for output
        
    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Generate filename
        filename = format_export_filename()
        filepath = os.path.join(memory.config.data_dir, filename)
        
        # Prepare export content
        export_content = []
        export_content.append("=" * 80)
        export_content.append("AI ARCHITECT BOT - CHAT EXPORT")
        export_content.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        export_content.append(f"Session Mode: {memory.current_prompt_type}")
        export_content.append("=" * 80)
        export_content.append("")
        
        # Add conversation history
        for i, message in enumerate(memory.conversations, 1):
            timestamp = message.get('timestamp', '')
            role = message['role'].upper()
            content = message['content']
            
            export_content.append(f"[{i:3d}] {timestamp} - {role}")
            export_content.append("-" * 40)
            export_content.append(content)
            export_content.append("")
        
        # Add session statistics
        stats = memory.get_statistics()
        export_content.append("=" * 80)
        export_content.append("SESSION STATISTICS")
        export_content.append("=" * 80)
        export_content.append(f"Total Messages: {stats['total_messages']}")
        export_content.append(f"User Messages: {stats['user_messages']}")
        export_content.append(f"Assistant Messages: {stats['assistant_messages']}")
        export_content.append(f"Estimated Tokens: {stats['estimated_tokens']}")
        export_content.append(f"Token Usage: {stats['token_usage_percentage']}")
        export_content.append("")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(export_content))
        
        console.print(f"[bold green]✓ Chat exported to: {filename}[/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]✗ Export failed: {e}[/bold red]")
        return False


def show_model_stats(engine: Any, console: Console):
    """Show model health statistics."""
    status = engine.get_status_summary()
    
    # Count model states
    healthy_count = len(status['available_models'])
    rate_limited_count = len(status['rate_limited_models'])
    busy_count = len(status['busy_models'])
    total = status['total_models']
    
    # Create stats table
    table = Table(title="Model Health Statistics", show_header=False, box=None)
    table.add_row("Total Models:", f"[bold]{total}[/bold]")
    table.add_row("Healthy:", f"[bold green]{healthy_count}[/bold green]")
    table.add_row("Rate Limited:", f"[bold red]{rate_limited_count}[/bold red]")
    table.add_row("Busy:", f"[bold yellow]{busy_count}[/bold yellow]")
    
    # Calculate health percentage
    health_percentage = (healthy_count / total * 100) if total > 0 else 0
    table.add_row("System Health:", f"[bold blue]{health_percentage:.1f}%[/bold blue]")
    
    console.print(table)


def clear_screen():
    """Clear the terminal screen for a clean startup."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def create_status_bar(engine: Any, memory: Any, session_id: str) -> str:
    """Create a status bar showing current system state."""
    status = engine.get_status_summary()
    current_model = status.get('current_model', 'Unknown')
    current_mode = memory.current_prompt_type
    healthy_count = len(status['available_models'])
    total_models = status['total_models']
    
    # Create status bar text
    status_text = f"🤖 Model: {current_model} | 📋 Mode: {current_mode} | 🏥 Health: {healthy_count}/{total_models} | 🔑 Session: {session_id[:8]}..."
    
    return status_text


def format_welcome_with_status(bot_name: str, session_id: str) -> Panel:
    """Format welcome message with session information."""
    welcome_text = Text()
    welcome_text.append("🚀 ", style="bold yellow")
    welcome_text.append(f"{bot_name}", style="bold cyan")
    welcome_text.append(" is ready!\n\n", style="bold")
    welcome_text.append("Session ID: ", style="dim")
    welcome_text.append(f"{session_id}", style="bold green")
    welcome_text.append("\n\nType '/help' for available commands.")
    
    return Panel(
        welcome_text,
        title="Welcome",
        border_style="blue",
        padding=(1, 2)
    )
