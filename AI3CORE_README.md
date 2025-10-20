# Ai3Core - Intelligent Decision Engine

**Version 1.0.0**

Ai3Core is a sophisticated multi-AI orchestration engine that intelligently routes tasks to the most appropriate AI model based on capabilities, performance metrics, and cost efficiency.

## Architecture

The system is built on **two independent stovepipes**:

### Stovepipe 1: Ai3Core (Decision Engine)
Pure business logic with no UI dependencies. Located in `ai3core/`.

**Modules:**

1. **Planner** (`ai3core/planner/`)
   - Decomposes prompts into task DAGs
   - Identifies dependencies
   - Extracts success criteria

2. **Capability Registry** (`ai3core/registry/`)
   - Tracks model skills and capabilities
   - Maintains rolling performance metrics
   - Supports custom model additions

3. **Router** (`ai3core/router/`)
   - Intelligent model selection using weighted scoring
   - Considers: skill match, performance, cost, context fit, features
   - Supports user overrides

4. **Executor** (`ai3core/executor/`)
   - Uniform interface across providers (Anthropic, OpenAI, xAI)
   - Retry logic and error handling
   - Token tracking and timing

5. **Verifier** (`ai3core/verifier/`)
   - Quality checks against success criteria
   - Failure pattern detection
   - Repair task generation

6. **Assembler** (`ai3core/assembler/`)
   - Synthesizes multiple artifacts
   - Deduplication and conflict resolution
   - Source attribution

7. **Journal & Artifact Store** (`ai3core/journal/`)
   - Persistent execution traces
   - Artifact storage and indexing
   - Replay and debugging support

### Stovepipe 2: Interface Layer
User-facing interfaces. Located in `interface/`.

- **CLI** (`interface/cli/`) - Command-line interface
- **VS Code Extension** - Future integration
- **Web API** - Future addition

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### Usage

**Process a prompt:**
```bash
python -m interface.cli.main "Write a Python function to calculate Fibonacci numbers"
```

**View statistics:**
```bash
python -m interface.cli.main --stats
```

**View history:**
```bash
python -m interface.cli.main --history --limit 5
```

**Replay a run:**
```bash
python -m interface.cli.main --replay <RUN_ID>
```

### Programmatic Usage

```python
from ai3core import Ai3Engine

# Initialize with API keys
engine = Ai3Engine(api_keys={
    "anthropic": "sk-...",
    "openai": "sk-...",
    "xai": "..."
})

# Process a prompt
response = engine.process("Explain quantum computing in simple terms")

print(response.content)
print(f"Confidence: {response.confidence}")
print(f"Sources: {response.source_artifacts}")

# Get statistics
stats = engine.get_stats()

# Set routing overrides
engine.set_routing_override("coding", "claude-3-7-sonnet-20250219")

# Get last trace
trace = engine.get_last_trace()
```

## Data Flow

```
User Prompt
    ↓
Planner → Task DAG
    ↓
Router → Model Selection (per task)
    ↓
Executor → Parallel Execution
    ↓
Verifier → Quality Checks
    ↓
Assembler → Final Response
    ↓
Journal → Persistence
```

## Model Capabilities

The system includes these models by default (configurable via `ai3core/registry/capabilities.json`):

- **Claude 3.7 Sonnet**: Best for coding, long documents, reasoning
- **GPT-4o**: Best for multimodal, data analysis, fast responses
- **Grok-3**: Best for mathematical reasoning, creative insights
- **GPT-4o-mini**: Fast and cost-effective for simpler tasks

## Routing Algorithm

Models are scored using a weighted function:

```
Score = 0.50 × skill_match
      + 0.20 × performance
      + 0.15 × cost_efficiency
      + 0.10 × context_fit
      + 0.05 × feature_support
```

**Weights are customizable** via `Router.update_weights()`.

## Persistence

### Run Journal
Complete execution traces stored in `.ai3_journal/`:
- Original prompt
- Task DAG
- All artifacts
- Verification results
- Final response
- Full metadata

### Artifact Store
Individual artifacts stored in `.ai3_artifacts/`:
- Indexed by task, model, date
- Searchable
- Retrievable for analysis

## Configuration

### Capabilities
Edit `ai3core/registry/capabilities.json` to:
- Add new models
- Update skill ratings
- Adjust cost/latency estimates

### Router Weights
Customize scoring weights:

```python
router.update_weights({
    "skill_match": 0.60,
    "performance": 0.20,
    "cost": 0.10,
    "context_fit": 0.05,
    "features": 0.05
})
```

### Custom Validators
Add task-specific validation:

```python
def validate_code(artifact, task):
    # Custom validation logic
    has_function = "def " in artifact.response
    return (1.0 if has_function else 0.5, has_function)

verifier = Verifier(custom_validators={
    "coding": validate_code
})
```

## Advanced Features

### Repair Tasks
Failed verifications can generate repair tasks automatically:

```python
if verification.needs_repair:
    repair_tasks = verifier.get_repair_tasks(verification, original_task)
```

### Telemetry Updates
The system automatically tracks:
- Success/error rates
- Average latencies
- Token usage
- Costs

Access via:
```python
metrics = registry.get_live_metrics("claude-3-7-sonnet-20250219")
```

### Replay & Debug
Replay any previous run:

```python
trace = engine.replay_run(run_id)

# Inspect plan
print(trace.plan.tasks)

# Inspect artifacts
for artifact in trace.artifacts:
    print(f"{artifact.model_id}: {artifact.response[:100]}")

# Inspect verifications
for verification in trace.verifications:
    print(f"{verification.artifact_id}: {verification.score}")
```

## Extensibility

### Adding a New Provider

1. Create adapter in `ai3core/executor/`:

```python
from .base import BaseExecutor

class NewProviderAdapter(BaseExecutor):
    def execute(self, task, model_id, **kwargs):
        # Implementation
        pass

    def validate_model(self, model_id):
        # Implementation
        pass
```

2. Update `ExecutorFactory`:

```python
if provider == ModelProvider.NEWPROVIDER:
    executor = NewProviderAdapter(api_key)
```

3. Add models to `capabilities.json`

### Adding a New Interface

Create in `interface/`:

```python
from ai3core import Ai3Engine

class WebAPI:
    def __init__(self, api_keys):
        self.engine = Ai3Engine(api_keys)

    def process_request(self, prompt):
        return self.engine.process(prompt)
```

## Performance

Typical performance metrics:
- **Planning**: <100ms
- **Routing**: <50ms per task
- **Execution**: Model-dependent (1-5s)
- **Verification**: <100ms per artifact
- **Assembly**: <100ms

Total overhead: ~300ms + model latency

## Testing

```bash
# Run basic test
python -m interface.cli.main "What is 2+2?"

# Test complex prompt
python -m interface.cli.main "Write a Python script to analyze CSV files, create visualizations, and generate a report"

# View results
python -m interface.cli.main --history
```

## Troubleshooting

**No API keys found:**
- Ensure `.env` file exists with valid keys
- Check environment variables are set

**Model not found:**
- Verify model ID in `capabilities.json`
- Check API key for that provider

**High error rates:**
- Check `engine.get_stats()` for telemetry
- Consider routing overrides

**Slow performance:**
- Review task decomposition
- Check model latencies in metrics
- Consider using faster models for simple tasks

## Future Enhancements

- [ ] LLM-based planning (vs rule-based)
- [ ] Parallel task execution
- [ ] Streaming responses
- [ ] Web UI dashboard
- [ ] API server
- [ ] Plugin system
- [ ] A/B testing framework
- [ ] Cost optimization mode

## Contributing

The system is designed for easy extension:
1. Core logic in `ai3core/` (Stovepipe 1)
2. Interfaces in `interface/` (Stovepipe 2)
3. Clean separation of concerns
4. Minimal dependencies

## License

MIT License - See LICENSE file

## Support

For issues or questions:
- Check the troubleshooting section
- Review the code documentation
- Open an issue in the repository
