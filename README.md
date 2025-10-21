# Ai3 Orchestrator - Production v2.1

Multi-LLM orchestration engine with intelligent routing, parallel execution, streaming, and self-verification.

## Features

- **LLM-Based Planning**: Generates dependency-aware task graphs using Claude
- **Parallel Execution**: Topologically-scheduled concurrent execution with concurrency controls
- **Streaming**: Server-Sent Events (SSE) for real-time progress
- **Self-Verification**: Quality checks with auto-repair and model fallback
- **Telemetry-Driven Routing**: Dynamic provider selection based on success rate, latency, and cost
- **Multi-Provider Support**: Anthropic (Claude), OpenAI (GPT-4), xAI (Grok 3/4)
- **CLI & API**: Both streaming and non-streaming interfaces

## Quick Start

### Installation

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management.

```bash
# Install uv if you haven't already
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Or if you prefer to use venv manually
uv venv
uv pip install -r requirements.txt
```

### Environment Variables

You can configure API keys using **either** method:

**Option 1: .env file (recommended)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_key_here
```

**Option 2: System environment variables**
```bash
# Linux/macOS
export ANTHROPIC_API_KEY=your_anthropic_key_here
export OPENAI_API_KEY=your_openai_key_here
export XAI_API_KEY=your_xai_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_anthropic_key_here"
$env:OPENAI_API_KEY="your_openai_key_here"
$env:XAI_API_KEY="your_xai_key_here"
```

**Optional Configuration**
```bash
AI3_PLANNER_MODEL=claude-3-7-sonnet-latest
AI3_MAX_CONCURRENCY=5
AI3_MAX_CONCURRENCY_PER_PROVIDER=3
AI3_VERIFY=on
AI3_REPAIR_LIMIT=1
```

Note: System environment variables take priority over .env file values.

### CLI Usage

```bash
# Non-streaming
uv run python -m interface.cli.main "Write a 3-section blog post about AI"

# Streaming with live progress
uv run python -m interface.cli.main "Write a 3-section blog post about AI" --stream

# Custom concurrency and model
uv run python -m interface.cli.main "Analyze this dataset" --stream --max-concurrency 10 --planner-model claude-3-7-sonnet-latest
```

### API Usage

```bash
# Start server
uv run uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# Non-streaming endpoint
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short story"}'

# Streaming endpoint (SSE)
curl -X POST http://localhost:8000/stream/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short story"}' \
  --no-buffer
```

## Architecture

### Core Components

**Ai3Core** - The orchestration engine with the following modules:

- **Planner** (`ai3core/planner/`) - LLM-based task decomposition and dependency graphs
- **Registry** (`ai3core/registry/`) - Model capabilities and telemetry tracking
- **Router** (`ai3core/router/`) - Intelligent provider selection with weighted scoring
- **Executor** (`ai3core/executor/`) - Parallel task execution with scheduler
- **Verifier** (`ai3core/verifier/`) - Quality checks, repair, and fallback logic
- **Assembler** (`ai3core/assembler/`) - Result synthesis and merging
- **Journal** (`ai3core/journal/`) - Run persistence and artifact storage
- **Telemetry** (`ai3core/telemetry/`) - Performance metrics collection

**Interface Layer**:
- **CLI** (`interface/cli/`) - Command-line interface
- **API** (`api/`) - FastAPI REST endpoints with streaming support

### Execution Flow

1. **Plan**: LLM generates TaskGraph (JSON schema-validated)
2. **Route**: Weighted scoring selects best provider per task (telemetry-informed)
3. **Execute**: Parallel execution respecting dependencies and concurrency limits
4. **Verify**: Quality checks with optional repair subtask or fallback to next-best model
5. **Assemble**: Merge artifacts into final output
6. **Journal**: Persist run trace and telemetry

### Supported Providers & Models

- **Anthropic**: Claude 3.7 Sonnet (200K context, excellent coding)
- **OpenAI**: GPT-4, GPT-3.5 Turbo (reliable general-purpose)
- **xAI**: Grok 3, Grok 4, Grok 4 Fast (2M context, advanced reasoning)

### Streaming Events

- `plan`: Planning started/completed
- `decision`: Provider selected for task
- `task_start`: Task execution begins
- `task_artifact`: Task produces output
- `task_verified`: Verification result
- `task_repaired`: Repair attempt
- `task_failed`: Task error
- `assemble_start`: Assembly begins
- `final`: Final output
- `stats`: Run statistics (cost, tokens, task count)

## Testing

```bash
# Run all tests
uv run pytest -q

# Specific test suites
uv run pytest tests/test_planner.py -v
uv run pytest tests/test_scheduler.py -v
uv run pytest tests/test_verifier_repair.py -v
```

## Configuration

All settings in `ai3core/settings.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| AI3_PLANNER_MODEL | claude-3-7-sonnet-latest | LLM for planning |
| AI3_PLANNER_MAXTOK | 4096 | Max tokens for planner |
| AI3_PLANNER_TEMPERATURE | 0.0 | Planner temperature |
| AI3_MAX_CONCURRENCY | 5 | Global concurrent tasks |
| AI3_MAX_CONCURRENCY_PER_PROVIDER | 3 | Per-provider limit |
| AI3_VERIFY | on | Enable verification |
| AI3_REPAIR_LIMIT | 1 | Max repair attempts |

## Project Structure

```
ai3_orchestrator/
├── ai3core/              # Core orchestration engine
│   ├── planner/         # Task planning and dependency graphs
│   ├── registry/        # Model capabilities database
│   ├── router/          # Provider selection logic
│   ├── executor/        # Parallel task execution
│   ├── providers/       # Provider adapters (Anthropic, OpenAI, xAI)
│   ├── verifier/        # Quality verification
│   ├── assembler/       # Result assembly
│   ├── journal/         # Persistence layer
│   └── telemetry/       # Metrics collection
├── interface/
│   └── cli/             # Command-line interface
├── api/                 # FastAPI REST endpoints
├── tests/               # Test suite
└── vscode-extension/    # VS Code extension (in development)
```

## Roadmap

- [x] LLM-based planner with JSON schema validation
- [x] Parallel execution with dependency awareness
- [x] Streaming via SSE
- [x] Verifier with repair and fallback
- [x] Telemetry-driven routing
- [x] xAI Grok integration
- [ ] VS Code extension integration
- [ ] Advanced assembly strategies (voting, ranked choice)
- [ ] Persistent caching layer
- [ ] Multi-modal support (image, audio)

## License

MIT
