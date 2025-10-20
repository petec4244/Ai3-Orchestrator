# Ai3 Orchestrator - Production v2.1

Multi-LLM orchestration engine with intelligent routing, parallel execution, streaming, and self-verification.

## Features

- **LLM-Based Planning**: Generates dependency-aware task graphs using Claude
- **Parallel Execution**: Topologically-scheduled concurrent execution with concurrency controls
- **Streaming**: Server-Sent Events (SSE) for real-time progress
- **Self-Verification**: Quality checks with auto-repair and model fallback
- **Telemetry-Driven Routing**: Dynamic provider selection based on success rate, latency, and cost
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

```bash
# Required
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here

# Optional
export AI3_PLANNER_MODEL=claude-3-7-sonnet-latest
export AI3_MAX_CONCURRENCY=5
export AI3_MAX_CONCURRENCY_PER_PROVIDER=3
export AI3_VERIFY=on
export AI3_REPAIR_LIMIT=1
```

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

### Two-Stovepipe Design

- **Ai3Core**: Orchestration engine (planner, router, executor, verifier, assembler, telemetry)
- **Interface**: CLI and future VS Code extension (no orchestration logic)

### Execution Flow

1. **Plan**: LLM generates TaskGraph (JSON schema-validated)
2. **Route**: Weighted scoring selects best provider per task (telemetry-informed)
3. **Execute**: Parallel execution respecting dependencies and concurrency limits
4. **Verify**: Quality checks with optional repair subtask or fallback to next-best model
5. **Assemble**: Merge artifacts into final output
6. **Journal**: Persist run trace and telemetry

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

## Roadmap

- [x] LLM-based planner with JSON schema validation
- [x] Parallel execution with dependency awareness
- [x] Streaming via SSE
- [x] Verifier with repair and fallback
- [x] Telemetry-driven routing
- [ ] VS Code extension integration
- [ ] Advanced assembly strategies (voting, ranked choice)
- [ ] Persistent caching layer
- [ ] Multi-modal support (image, audio)

## License

MIT
