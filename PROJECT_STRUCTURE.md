# AI3 Orchestrator - Project Structure

## Directory Tree

```
ai3-orchestrator/
│
├── backend/                          # Python backend for AI orchestration
│   ├── main.py                       # Main orchestrator entry point
│   ├── task_analyzer.py              # Prompt analysis & categorization
│   ├── api_clients.py                # API wrappers (Grok, Claude, ChatGPT)
│   ├── config.py                     # Configuration management
│   ├── task_rules.json               # Task routing rules (editable)
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment variables template
│
├── vscode-extension/                 # VS Code extension
│   ├── src/
│   │   └── extension.ts              # Extension logic & commands
│   ├── package.json                  # Extension manifest
│   ├── tsconfig.json                 # TypeScript config
│   └── .vscodeignore                 # Package exclusions
│
├── docs/                             # Documentation
│   └── AIOrchestratorDocs.tsx        # React documentation component
│
├── README.md                         # Main documentation
└── PROJECT_STRUCTURE.md              # This file
```

## File Summary

### Backend (Python)

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 266 | Main orchestrator class and CLI entry point |
| `task_analyzer.py` | 123 | Analyzes prompts and categorizes tasks |
| `api_clients.py` | 118 | API client wrappers with retry logic |
| `config.py` | 60 | Configuration management |
| `task_rules.json` | 12 | Task routing configuration (JSON) |
| `requirements.txt` | 4 | Python dependencies |
| `.env.example` | 3 | Environment variables template |

### VS Code Extension (TypeScript)

| File | Lines | Purpose |
|------|-------|---------|
| `extension.ts` | 313 | Extension entry point, commands, webviews |
| `package.json` | 53 | Extension manifest and metadata |
| `tsconfig.json` | 21 | TypeScript compiler configuration |
| `.vscodeignore` | 10 | Files to exclude from VSIX package |

### Documentation

| File | Lines | Purpose |
|------|-------|---------|
| `README.md` | ~350 | Complete setup and usage guide (v2.0) |
| `AI_ROUTING_GUIDE.md` | ~650 | Evidence-based routing documentation |
| `QUICK_REFERENCE.md` | ~300 | Quick decision tree and examples |
| `AIOrchestratorDocs.tsx` | 155 | Interactive React documentation |
| `PROJECT_STRUCTURE.md` | This file | Project structure overview |

## Quick Start

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Test Backend**
   ```bash
   python main.py "Write a hello world function"
   ```

3. **Extension Setup**
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```

4. **Run Extension**
   - Open `vscode-extension` folder in VS Code
   - Press F5 to launch Extension Development Host
   - Or: `npm run package` then install the .vsix file

## Key Features

- **Multi-Model Orchestration**: Routes tasks to Grok, Claude, or ChatGPT
- **Intelligent Analysis**: Categorizes prompts into coding, summarization, data analysis, etc.
- **Grok → Claude Pipeline**: Grok refines coding prompts, Claude executes
- **VS Code Integration**: Native extension with keyboard shortcuts
- **Configurable**: JSON-based routing rules
- **Error Handling**: Automatic retries with exponential backoff

## Task Categories (v2.0 - 12 Categories)

**Claude-Optimized:**
- **coding** → claude (production quality, SWE-bench leader)
- **creative_writing** → claude (engaging narratives, 200K context)
- **professional_writing** → claude (technical docs, specifications)
- **document_processing** → claude (200K context window)
- **automation** → claude (desktop/GUI automation)

**ChatGPT-Optimized:**
- **summarization** → chatgpt (efficient extraction)
- **data_analysis** → chatgpt (visualization, BI)
- **multimodal** → chatgpt (image/voice/video generation)
- **integration** → chatgpt (APIs, webhooks, Zapier)
- **general** → chatgpt (versatile Swiss Army knife)

**Grok-Optimized:**
- **mathematical_reasoning** → grok (93.3% AIME)
- **realtime_social** → grok (native X/Twitter)
- **creative_insight** → grok (brainstorming, unique perspectives)

## Next Steps

1. Add your API keys to `backend/.env`
2. Customize routing rules in `backend/task_rules.json`
3. Test the system with various prompts
4. Install the VS Code extension for integrated workflow

---

## What's New in v2.0

- **12 Task Categories**: Expanded from 5 to 12 specialized categories
- **150+ Keywords**: Comprehensive keyword matching based on AI benchmarks
- **Direct Claude Routing**: Optimized for production code (removed mandatory Grok refinement)
- **Evidence-Based**: Routing decisions backed by independent benchmark analysis
- **New Categories**:
  - Mathematical reasoning (Grok 93.3% AIME)
  - Multimodal tasks (ChatGPT native voice/video/image)
  - Real-time social intelligence (Grok native X access)
  - Document processing (Claude 200K context)
  - Professional writing (Claude technical docs)
  - Automation (Claude desktop/GUI control)
  - Creative insights (Grok brainstorming)
  - Integration (ChatGPT Zapier ecosystem)

---

**AI3 Orchestrator v2.0.0** - "Evidence-Based Multi-Model Orchestration"
