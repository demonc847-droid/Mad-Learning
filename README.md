# AI Architect Bot

A sophisticated terminal-based AI assistant that intelligently rotates between multiple LLM models to provide optimal responses while maintaining conversational context.

## Features

- **Multi-Model Rotation**: Automatically switches between different AI models based on availability and performance
- **Context Management**: Intelligent memory system that prunes old conversations to stay within token limits
- **Rich Terminal UI**: Beautiful command-line interface with real-time feedback
- **Persistent History**: JSON-based conversation storage for continuity across sessions
- **Error Handling**: Robust fallback mechanisms and detailed logging
- **Specialized Prompts**: Different system instructions for various use cases

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ai_architect_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

4. Run the bot:
   ```bash
   python src/main.py
   ```

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `BOT_NAME`: Name displayed in the terminal (default: AI_Architect_Bot)
- `MAX_CONTEXT_TOKENS`: Maximum tokens for context window (default: 8192)
- `MAX_HISTORY_MESSAGES`: Maximum number of messages to keep in history (default: 50)
- `TEMPERATURE`: Creativity parameter for model responses (default: 0.7)
- `TOP_P`: Nucleus sampling parameter (default: 0.9)

### Model Selection

The bot supports multiple models with automatic fallback:

**Primary Models:**
- `qwen/qwen-2-72b-instruct` - Qwen 2 72B Instruct (default)
- `anthropic/claude-sonnet-4-2025` - Claude Sonnet 4
- `google/gemini-pro` - Gemini Pro
- `openai/gpt-4o-mini` - GPT-4o Mini
- `meta-llama/llama-3.1-sonar-large-32k-chat` - Llama 3.1 Sonar

**Fallback Strategy:**
1. Try primary model first
2. If unavailable, cycle through fallback models
3. If all fail, use the last working model

## Usage

### Basic Commands

- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/models` - Show current model status
- `/prompt <type>` - Switch to a different system prompt
- `/exit` - Exit the bot

### Specialized Prompts

The bot includes several specialized system prompts:

- **architect** - General-purpose AI architect (default)
- **police_cam** - Video analysis and description
- **coder** - Python and coding assistance

### Example Session

```
$ python src/main.py
🤖 AI_Architect_Bot: Hello! How can I help you today?

You: Help me design a REST API for a task management application.

🤖 AI_Architect_Bot: I'll help you design a REST API for task management. Let me switch to a coding-focused prompt...

[Switching to coder prompt...]

🤖 AI_Architect_Bot: Great! For a task management API, I recommend these endpoints:

1. **Users**: POST /api/users, GET /api/users/{id}
2. **Projects**: POST /api/projects, GET /api/projects
3. **Tasks**: POST /api/tasks, GET /api/tasks/{id}, PUT /api/tasks/{id}, DELETE /api/tasks/{id}
4. **Authentication**: POST /api/auth/login, POST /api/auth/logout

Would you like me to elaborate on any specific part?
```

## Project Structure

```
ai_architect_bot/
├── .env                # Private: OpenRouter API Key & sensitive configs
├── .gitignore          # Keeps .env and __pycache__ out of GitHub
├── README.md           # Setup instructions & model list
├── requirements.txt    # dependencies (rich, python-dotenv, requests)
│
├── data/               # Persistent storage
│   ├── history.json    # Conversational memory
│   └── error.log       # Debugging logs for connectivity issues
│
├── src/                # Source code directory
│   ├── __init__.py     # Makes 'src' a Python package
│   ├── main.py         # Entry point: The Terminal UI (Rich) & Loop
│   ├── config.py       # Loads .env and defines Model List
│   ├── models.py       # The Rotation Engine & Health checks
│   ├── memory.py       # Context pruning & JSON save/load logic
│   └── utils.py        # Formatting, Spinners, and Command Handlers
│
└── prompts/            # System Instruction Library
    ├── architect.txt   # Default system prompt
    ├── police_cam.txt  # Specialized analysis prompt
    └── coder.txt       # Python/Qwen-specific prompt
```

## Dependencies

- `rich` - Beautiful terminal formatting
- `python-dotenv` - Environment variable management
- `requests` - HTTP client for API calls

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `OPENROUTER_API_KEY` is valid and has sufficient credits
2. **Model Unavailable**: The bot will automatically try fallback models
3. **Context Too Long**: Old messages are automatically pruned to stay within token limits

### Logs

Check `data/error.log` for detailed error information and debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the error logs in `data/error.log`
- Verify your API key and model availability
- Ensure all dependencies are installed