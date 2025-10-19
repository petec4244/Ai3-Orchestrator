# AI3 Orchestrator System

**"One Source to Rule Them All"**

A sophisticated multi-AI model orchestration system that intelligently analyzes prompts, breaks them into tasks, and routes them to the optimal AI models (Grok, Claude, ChatGPT) for processing.

## Features

- **Intelligent Task Analysis**: Automatically categorizes prompts into task types (coding, summarization, data analysis, creative writing, general)
- **Multi-Model Orchestration**: Routes tasks to the most appropriate AI model
- **Grok → Claude Pipeline**: Special workflow for coding tasks where Grok refines prompts and Claude executes
- **Error Handling**: Automatic retries with exponential backoff
- **Configurable Routing**: JSON-based configuration for flexible task routing
- **VS Code Extension**: Native VS Code integration with keyboard shortcuts
- **Progress Tracking**: Visual feedback with webview panels

## Project Structure

```
ai3-orchestrator/
├── backend/
│   ├── main.py              # Main orchestrator logic
│   ├── task_analyzer.py     # Prompt analysis and task breakdown
│   ├── api_clients.py       # API client wrappers for Grok, Claude, ChatGPT
│   ├── config.py            # Configuration management
│   ├── requirements.txt     # Python dependencies
│   ├── task_rules.json      # Task routing configuration
│   └── .env.example         # Environment variables template
├── vscode-extension/
│   ├── src/
│   │   └── extension.ts     # VS Code extension entry point
│   ├── package.json         # Extension manifest
│   ├── tsconfig.json        # TypeScript configuration
│   └── .vscodeignore        # Package exclusions
├── docs/
│   └── AIOrchestratorDocs.tsx  # React documentation component
└── README.md                # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- VS Code (for extension development)
- API keys for:
  - xAI (Grok)
  - OpenAI (ChatGPT)
  - Anthropic (Claude)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```
   XAI_API_KEY=your_xai_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. **Test the backend**
   ```bash
   python main.py "Write a Python function to calculate fibonacci numbers"
   ```

### VS Code Extension Setup

1. **Navigate to extension directory**
   ```bash
   cd vscode-extension
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Compile TypeScript**
   ```bash
   npm run compile
   ```

4. **Run in development mode**

   Open the `vscode-extension` folder in VS Code and press `F5` to launch the Extension Development Host.

5. **Package and install (optional)**
   ```bash
   npm run package
   code --install-extension ai3-orchestrator-*.vsix
   ```

## Usage

### Command Line

Run the orchestrator directly from command line:

```bash
cd backend
python main.py "Your prompt here"
```

Example:
```bash
python main.py "Write a Python function to parse CSV files, then summarize the data"
```

### VS Code Extension

1. **Open Command Palette**: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. **Run**: Type "AI3: Process Prompt"
3. **Or use keyboard shortcut**: `Ctrl+Shift+A` (or `Cmd+Shift+A` on Mac)
4. **Enter your prompt** in the input box
5. **View results** in the webview panel

### Opening Configuration

To modify task routing rules:
- Command Palette → "AI3: Open Configuration"
- Or edit `backend/task_rules.json` directly

## Configuration

### Task Routing Rules

Edit `backend/task_rules.json` to customize how tasks are routed:

```json
{
  "routing_rules": {
    "coding": "grok_refine_then_claude",
    "summarization": "chatgpt",
    "data_analysis": "chatgpt",
    "creative_writing": "grok",
    "general": "grok"
  },
  "settings": {
    "max_retries": 3,
    "timeout_seconds": 60,
    "enable_logging": true
  }
}
```

### Routing Options

Based on comprehensive AI model comparison analysis:

- `claude`: Route directly to Claude (best for coding, writing, document processing, automation)
- `chatgpt`: Route directly to ChatGPT (best for multimodal, data analysis, summarization, integration)
- `grok`: Route directly to Grok (best for math/STEM, real-time social intelligence, creative insights)
- `grok_refine_then_claude`: Legacy option - Grok refines the prompt, then Claude executes

**Current Routing Configuration:**
- coding → Claude (SWE-bench leader, production quality)
- mathematical_reasoning → Grok (93.3% AIME vs 33-36% for others)
- multimodal → ChatGPT (only native image/voice/video generation)
- realtime_social → Grok (native X/Twitter integration)
- creative_writing → Claude (best narrative flow, human-like prose)
- data_analysis → ChatGPT (visualization, statistics, BI)
- integration → ChatGPT (5000+ apps via Zapier)
- professional_writing → Claude (technical docs, specifications)
- document_processing → Claude (200K context window)
- automation → Claude (desktop/UI automation)
- creative_insight → Grok (unique perspectives, brainstorming)
- summarization → ChatGPT (efficient extraction)
- general → ChatGPT (most versatile "Swiss Army knife")

## How It Works

1. **Prompt Analysis**: The `TaskAnalyzer` examines your prompt and categorizes it
2. **Task Breakdown**: Multi-part prompts are split into individual tasks
3. **Routing**: Each task is routed to the optimal AI model based on configuration
4. **Processing**: Tasks are processed sequentially or in parallel
5. **Combination**: Results are combined into a cohesive final output

### Example Workflow

**Prompt**: "Write a Python function to parse CSV files, then summarize the data"

1. Analyzer identifies 2 tasks:
   - Task 1: "Write a Python function to parse CSV files" → coding
   - Task 2: "summarize the data" → summarization

2. Routing:
   - Task 1 → `grok_refine_then_claude` (Grok refines → Claude codes)
   - Task 2 → `chatgpt`

3. Output: Combined response with both the code and the summary

## Task Categories

The analyzer categorizes tasks based on 150+ keywords across 12 specialized categories:

### **Claude-Optimized Categories**
- **coding**: Production-quality code, refactoring, debugging, software engineering
- **creative_writing**: Stories, narratives, long-form content, engaging prose
- **professional_writing**: Technical docs, API specs, business writing, compliance
- **document_processing**: PDF analysis, book summaries, 200K context tasks
- **automation**: Desktop automation, GUI control, RPA, workflow orchestration

### **ChatGPT-Optimized Categories**
- **summarization**: Summaries, TL;DR, overviews, information extraction
- **data_analysis**: Statistics, visualization, Excel, analytics, forecasting
- **multimodal**: Image generation, voice, video, DALL-E, transcription
- **integration**: API integration, webhooks, Zapier, third-party services

### **Grok-Optimized Categories**
- **mathematical_reasoning**: Math proofs, STEM, calculus, scientific research
- **realtime_social**: Twitter/X analysis, sentiment, trending, social listening
- **creative_insight**: Brainstorming, unique perspectives, innovative solutions

### **Default Category**
- **general**: Versatile general-purpose tasks (routed to ChatGPT)

**See [AI_ROUTING_GUIDE.md](docs/AI_ROUTING_GUIDE.md) for complete keyword lists and routing logic.**

## API Clients

### GrokClient
- Base URL: `https://api.x.ai/v1`
- Model: `grok-beta`
- Special feature: `refine_prompt()` for enhanced prompt engineering

### ClaudeClient
- Uses Anthropic SDK
- Model: `claude-sonnet-4-20250514`
- Max tokens: 4000 (configurable)

### ChatGPTClient
- Uses OpenAI SDK
- Model: `gpt-4-turbo-preview`
- Max tokens: 2000 (configurable)

## Error Handling

All API clients include:
- Automatic retry logic (default: 3 attempts)
- Exponential backoff (2^attempt seconds)
- Comprehensive logging
- Graceful fallbacks

## Logging

Logs are written to:
- Console output (stdout)
- File: `backend/orchestrator.log`

Configure logging in `backend/main.py` or via `task_rules.json` settings.

## Development

### Adding New AI Models

1. Create a new client class in `api_clients.py` extending `BaseAPIClient`
2. Implement the `complete()` method
3. Add routing rules in `task_rules.json`
4. Update `main.py` to initialize the new client

### Adding New Task Categories

1. Add keywords in `task_analyzer.py`
2. Add routing rule in `task_rules.json`
3. Update documentation

## Troubleshooting

### "Module not found" errors
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

### "API key not found" errors
- Check that `.env` file exists in the backend directory
- Verify API keys are set correctly
- Ensure `python-dotenv` is installed

### Extension not loading
- Run `npm run compile` in vscode-extension directory
- Check VS Code Developer Tools (Help → Toggle Developer Tools)
- Verify Python is in system PATH

### Python backend not found
- Ensure backend folder is in your workspace
- Check extension output channel for path information
- Adjust backend path in `extension.ts` if needed

## Contributing

This is part of the AI Trinity orchestration system. For enhancements:
1. Test changes thoroughly with all three AI models
2. Update routing rules documentation
3. Add logging for new features
4. Update this README

## License

Proprietary - Part of Pete's Code AI Trinity System

## Version History

- **v2.0.0** (2025-01-16): Evidence-Based Routing System
  - Expanded from 5 to 12 specialized task categories
  - Added 150+ keywords based on AI comparison analysis
  - Direct Claude routing (production-quality code)
  - Mathematical reasoning → Grok (93.3% AIME)
  - Multimodal tasks → ChatGPT (DALL-E, voice, video)
  - Real-time social intelligence → Grok (native X access)
  - Document processing → Claude (200K context)
  - Routing based on independent benchmark verification
  - New unconventional use cases documented
  - Comprehensive [AI Routing Guide](docs/AI_ROUTING_GUIDE.md)

- **v1.0.0** (2025-01-16): Initial release
  - Multi-model orchestration
  - VS Code extension
  - Task analysis and routing
  - Grok → Claude pipeline for coding tasks

## Support

For issues or questions:
- Check the logs in `backend/orchestrator.log`
- Review VS Code Output channel: "AI Orchestrator"
- Verify API keys and internet connectivity

---

**AI3 Orchestrator** - Intelligent Multi-Model Task Distribution
