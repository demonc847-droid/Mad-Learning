# Mad Learning

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Rich](https://img.shields.io/badge/Rich-13.0+-green.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-9cf.svg)
![Terminal](https://img.shields.io/badge/Terminal-Rich%20UI-orange.svg)

A sophisticated terminal-based AI assistant that intelligently rotates between multiple LLM models to provide optimal responses while maintaining conversational context.

## 🚀 Features

### 🤖 Multi-Model Rotation
- **Intelligent Failover**: Automatically switches between different AI models based on availability and performance
- **Health Monitoring**: Real-time model status tracking with cooldown timers for rate-limited models
- **Karachi Internet Optimized**: Enhanced timeout handling for reliable performance in challenging network conditions

### 💾 Smart Context Management
- **Intelligent Memory**: Automatic conversation pruning to stay within token limits
- **Persistent History**: JSON-based conversation storage for continuity across sessions
- **Context Optimization**: Smart message retention prioritizing recent and relevant conversations

### 🎨 Rich Terminal UI
- **Professional Interface**: Beautiful command-line interface with real-time feedback
- **Visual Indicators**: Status bars, progress spinners, and model health indicators
- **Export Capabilities**: Export chat history to formatted text files

### 🎯 Specialized Prompts
- **Architect Mode**: General-purpose AI architect for software design and system architecture
- **Coder Mode**: Python and coding assistance with best practices and modern techniques
- **Police Cam Mode**: Video analysis and description for surveillance footage

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- OpenRouter API key

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone git@github.com:demonc847-droid/Mad-Learning.git
   cd Mad-Learning
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ai_architect_bot/requirements.txt
   ```

3. **Configure your API key:**
   ```bash
   cp ai_architect_bot/.env.template ai_architect_bot/.env
   # Edit .env and add your OpenRouter API key
   ```

4. **Run the bot:**
   ```bash
   python ai_architect_bot/src/main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `ai_architect_bot/` directory with the following variables:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Bot Configuration
BOT_NAME=Mad_Learning_Bot
MAX_CONTEXT_TOKENS=8192
MAX_HISTORY_MESSAGES=50
TEMPERATURE=0.7
TOP_P=0.9

# Model Selection
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=anthropic/claude-sonnet-4.6,google/gemini-3.1-pro-preview,qwen/qwen3.5-35b-a3b
```

### Supported Models

The bot supports multiple models with automatic fallback:

**Primary Models:**
- `openai/gpt-4o-mini` - Fast and cost-effective
- `anthropic/claude-sonnet-4.6` - Excellent reasoning capabilities
- `google/gemini-3.1-pro-preview` - Strong multimodal understanding
- `qwen/qwen3.5-35b-a3b` - Powerful open-source alternative

**Fallback Strategy:**
1. Try primary model first
2. If unavailable, cycle through fallback models
3. If all fail, use the last working model

## 🎮 Usage

### Basic Commands

- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/models` - Show current model status
- `/prompt <type>` - Switch to a different system prompt
- `/status` - Show bot status and statistics
- `/export` - Export chat history to text file
- `/stats` - Show model health statistics
- `/exit` - Exit the bot

### Specialized Prompts

Switch between different AI personas:

```bash
/prompt architect    # General-purpose AI architect
/prompt coder        # Python and coding assistance
/prompt police_cam   # Video analysis and description
```

### Example Session

```
$ python ai_architect_bot/src/main.py
🤖 Mad_Learning_Bot: Hello! How can I help you today?

You: Help me design a REST API for a task management application.

🤖 Mad_Learning_Bot: I'll help you design a REST API for task management. Let me switch to a coding-focused prompt...

[Switching to coder prompt...]

🤖 Mad_Learning_Bot: Great! For a task management API, I recommend these endpoints:

1. **Users**: POST /api/users, GET /api/users/{id}
2. **Projects**: POST /api/projects, GET /api/projects
3. **Tasks**: POST /api/tasks, GET /api/tasks/{id}, PUT /api/tasks/{id}, DELETE /api/tasks/{id}
4. **Authentication**: POST /api/auth/login, POST /api/auth/logout

Would you like me to elaborate on any specific part?
```

## 📁 Project Structure

```
Mad-Learning/
└── ai_architect_bot/
    ├── .env.template           # Environment variable template
    ├── .gitignore             # Git ignore rules
    ├── README.md              # Setup instructions & model list
    ├── requirements.txt       # Dependencies
    │
    ├── data/                  # Persistent storage
    │   ├── history.json       # Conversational memory
    │   └── error.log          # Debugging logs
    │
    ├── src/                   # Source code
    │   ├── __init__.py        # Package initialization
    │   ├── main.py            # Entry point with Rich UI
    │   ├── config.py          # Configuration management
    │   ├── models.py          # Model rotation engine
    │   ├── memory.py          # Context management
    │   └── utils.py           # Utility functions
    │
    └── prompts/               # System instruction library
        ├── architect.txt      # Default system prompt
        ├── coder.txt          # Python/Qwen-specific prompt
        └── police_cam.txt     # Video analysis prompt
```

## 🛠️ Dependencies

- **rich** - Beautiful terminal formatting and progress bars
- **python-dotenv** - Environment variable management
- **requests** - HTTP client for API calls
- **colorama** - Cross-platform colored terminal text (Windows support)

## 🔧 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `OPENROUTER_API_KEY` is valid and has sufficient credits
2. **Model Unavailable**: The bot will automatically try fallback models
3. **Context Too Long**: Old messages are automatically pruned to stay within token limits
4. **Network Issues**: The bot includes enhanced timeout handling for slow connections

### Logs

Check `ai_architect_bot/data/error.log` for detailed error information and debugging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Support

For issues and questions:
- Check the error logs in `ai_architect_bot/data/error.log`
- Verify your API key and model availability
- Ensure all dependencies are installed

## 📞 Contact

For support and inquiries, please open an issue in the repository.

---

**Mad Learning** - Where AI meets intelligent conversation management. 🚀