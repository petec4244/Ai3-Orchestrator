# Ai3 Orchestrator - Architecture Documentation

## Version 2.1

This document provides detailed technical architecture documentation for the Ai3 Orchestrator v2.1.

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [System Architecture](#system-architecture)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [Provider System](#provider-system)
7. [Configuration](#configuration)
8. [Telemetry & Metrics](#telemetry--metrics)

---

## Overview

Ai3 Orchestrator is a production-grade multi-LLM orchestration engine that intelligently routes tasks to the most appropriate AI model based on capabilities, performance metrics, and cost efficiency. The system supports parallel execution, streaming responses, quality verification, and self-repair.

### Key Capabilities

- **Multi-Provider Support**: Anthropic, OpenAI, xAI
- **Intelligent Routing**: Telemetry-driven provider selection
- **Parallel Execution**: Dependency-aware concurrent task execution
- **Quality Assurance**: Automated verification with repair and fallback
- **Streaming**: Real-time progress via Server-Sent Events
- **Persistence**: Complete run traces and artifact storage

---

## Core Principles

### 1. Separation of Concerns

The system follows a strict two-layer architecture:

- **Ai3Core**: Pure orchestration logic, no UI dependencies
- **Interface Layer**: User-facing interfaces (CLI, API)

### 2. Provider Agnostic

All LLM providers are abstracted behind a common interface, making it easy to add new providers without modifying core logic.

### 3. Telemetry-Driven Decisions

Routing decisions are informed by real-time performance metrics:
- Success/error rates
- Latency measurements
- Cost tracking
- Model capabilities

### 4. Fail-Safe Operations

Multiple layers of error handling:
- Provider failover
- Repair task generation
- Fallback to alternative models
- Graceful degradation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Interface Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     CLI      │  │  FastAPI     │  │   VS Code    │      │
│  │  (Streaming) │  │  (REST/SSE)  │  │  (Future)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          └─────────────────┴──────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Ai3Core Engine                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Planner                                          │  │
│  │     • LLM-based task decomposition                   │  │
│  │     • Dependency graph generation                    │  │
│  │     • JSON schema validation                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │  2. Router                                          │   │
│  │     • Telemetry-based provider selection            │   │
│  │     • Weighted scoring (skill, cost, latency)       │   │
│  │     • Capability matching                            │   │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │  3. Executor (Scheduler)                            │   │
│  │     • Parallel task execution                        │   │
│  │     • Dependency resolution                          │   │
│  │     • Concurrency limiting                           │   │
│  │     • Provider adapters                              │   │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │  4. Verifier                                        │   │
│  │     • Quality checks                                 │   │
│  │     • Repair task generation                         │   │
│  │     • Fallback to alternative models                 │   │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │  5. Assembler                                       │   │
│  │     • Result synthesis                               │   │
│  │     • Artifact merging                               │   │
│  │     • Final output generation                        │   │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────▼──────────────────────────┐   │
│  │  6. Journal & Telemetry                             │   │
│  │     • Run persistence                                │   │
│  │     • Artifact storage                               │   │
│  │     • Metrics collection                             │   │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    Provider Adapters                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Anthropic  │  │   OpenAI    │  │     xAI     │         │
│  │   (Claude)  │  │   (GPT-4)   │  │   (Grok)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Planner (`ai3core/planner/`)

**Purpose**: Decomposes user prompts into structured task graphs.

**Key Files**:
- `llm_planner.py` - LLM-based planning using Claude
- `planner.py` - Task graph construction

**Responsibilities**:
- Parse user prompts
- Generate task dependency graphs (DAGs)
- Extract success criteria per task
- Validate task structures

**Output**: TaskGraph with nodes and dependencies

### 2. Registry (`ai3core/registry/`)

**Purpose**: Maintains model capabilities and performance metrics.

**Key Files**:
- `registry.py` - Capability registry
- `loader.py` - Load capabilities from JSON
- `capabilities.json` - Model definitions

**Model Information**:
- Skill ratings (reasoning, coding, creative writing, etc.)
- Context windows
- Cost per 1K tokens
- Feature support (streaming, vision, function calling)
- Live performance metrics (success rate, latency)

**Supported Models**:
- Anthropic: Claude 3.7 Sonnet
- OpenAI: GPT-4, GPT-3.5 Turbo
- xAI: Grok 3, Grok 4, Grok 4 Fast, Grok 4 Fast Reasoning

### 3. Router (`ai3core/router/`)

**Purpose**: Intelligent provider selection for each task.

**Key Files**:
- `router.py` - Routing logic
- `selector.py` - Provider selection algorithm

**Routing Algorithm**:

```python
score = (
    0.50 × skill_match +
    0.20 × performance +
    0.15 × cost_efficiency +
    0.10 × context_fit +
    0.05 × feature_support
)
```

**Factors Considered**:
- Task type and required skills
- Model capabilities from registry
- Live telemetry (success rate, latency)
- Cost efficiency
- Context window requirements
- Feature requirements (streaming, vision)

### 4. Executor (`ai3core/executor/`)

**Purpose**: Execute tasks in parallel with dependency management.

**Key Files**:
- `scheduler.py` - Parallel execution scheduler
- `base.py` - Base executor interface
- `anthropic_adapter.py` - Claude provider adapter
- `openai_adapter.py` - OpenAI provider adapter
- `xai_adapter.py` - xAI Grok provider adapter
- `executor_factory.py` - Provider instantiation

**Features**:
- Topological task ordering
- Concurrent execution with limits
- Per-provider rate limiting
- Automatic retries with exponential backoff
- Token usage tracking

**Concurrency Controls**:
- Global max concurrency (default: 5)
- Per-provider limits (default: 3)
- Dependency-aware scheduling

### 5. Verifier (`ai3core/verifier/`)

**Purpose**: Quality assurance and error recovery.

**Key Files**:
- `verifier.py` - Verification logic
- `verify.py` - Verification utilities

**Verification Steps**:
1. Check artifact against success criteria
2. Pattern detection for common failures
3. Generate repair tasks if needed
4. Fallback to alternative models
5. Confidence scoring

**Repair Strategies**:
- Generate subtasks to fix issues
- Re-execute with different model
- Merge partial results

### 6. Assembler (`ai3core/assembler/`)

**Purpose**: Synthesize multiple artifacts into final output.

**Key Files**:
- `assembler.py` - Assembly orchestration
- `strategies.py` - Assembly strategies

**Assembly Strategies**:
- **Concatenate**: Merge all artifacts in order
- **Best Single**: Select highest-quality artifact
- **Synthesize**: LLM-based synthesis of multiple outputs
- **Consensus**: Vote-based selection (future)

### 7. Journal & Telemetry (`ai3core/journal/`, `ai3core/telemetry/`)

**Purpose**: Persistence and metrics collection.

**Key Files**:
- `store.py` - Journal storage
- `run_journal.py` - Run trace persistence
- `artifact_store.py` - Artifact management
- `metrics.py` - Telemetry collection

**Stored Data**:
- Complete run traces
- All task artifacts
- Verification results
- Performance metrics
- Cost tracking
- Error logs

**Metrics Tracked**:
- Success/error rates per model
- Average latency per model
- Token usage and costs
- Task completion times
- Concurrency levels

---

## Data Flow

### Typical Request Flow

```
1. User submits prompt via CLI/API
   │
   ▼
2. Planner decomposes into TaskGraph
   • Creates tasks with dependencies
   • Extracts success criteria
   │
   ▼
3. Router selects provider for each task
   • Queries registry for capabilities
   • Checks telemetry metrics
   • Calculates weighted scores
   │
   ▼
4. Scheduler executes tasks in parallel
   • Respects dependencies
   • Limits concurrency
   • Streams progress events
   │
   ▼
5. Verifier checks each artifact
   • Validates against criteria
   • Generates repair tasks if needed
   • Falls back to alternative models
   │
   ▼
6. Assembler synthesizes final output
   • Merges artifacts
   • Calculates confidence
   • Attributes sources
   │
   ▼
7. Journal persists run trace
   • Stores artifacts
   • Records metrics
   • Updates telemetry
   │
   ▼
8. Return final response to user
```

### Streaming Flow

```
User Request
   │
   ▼
┌────────────────────────────────────┐
│  FastAPI SSE Endpoint              │
│  or CLI with --stream flag         │
└────────────┬───────────────────────┘
             │
             ▼
    Ai3Core.run_async_stream()
             │
             ├─► Event: plan_start
             ├─► Event: plan_complete
             │
             ├─► Event: decision (per task)
             │
             ├─► Event: task_start (per task)
             ├─► Event: task_artifact (per task)
             ├─► Event: task_verified (per task)
             ├─► Event: task_repaired (if needed)
             ├─► Event: task_failed (if error)
             │
             ├─► Event: assemble_start
             │
             ├─► Event: final
             └─► Event: stats
```

---

## Provider System

### Provider Abstraction

All providers implement a common interface:

```python
class BaseProvider:
    async def execute(self, prompt: str, **kwargs) -> Dict:
        """Execute prompt and return response."""
        pass

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        pass
```

### Adding a New Provider

To add a new LLM provider:

1. **Create adapter** in `ai3core/providers/`:
   ```python
   # ai3core/providers/newprovider.py
   class NewProvider(BaseProvider):
       async def execute(self, prompt, **kwargs):
           # Implementation
           pass
   ```

2. **Add to capabilities.json**:
   ```json
   {
     "models": {
       "newprovider-model": {
         "provider": "newprovider",
         "skills": {...},
         "context_window": 100000,
         "cost_per_1k_tokens": 0.002
       }
     }
   }
   ```

3. **Update engine** in `ai3core/engine.py`:
   ```python
   def _get_provider_instance(self, provider_name: str):
       if "newprovider" in provider_name.lower():
           return NewProvider()
   ```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | required | Anthropic API key |
| `OPENAI_API_KEY` | required | OpenAI API key |
| `XAI_API_KEY` | required | xAI API key |
| `AI3_PLANNER_MODEL` | claude-3-7-sonnet-latest | Model for planning |
| `AI3_PLANNER_MAXTOK` | 4096 | Max tokens for planner |
| `AI3_PLANNER_TEMPERATURE` | 0.0 | Planner temperature |
| `AI3_MAX_CONCURRENCY` | 5 | Global concurrent tasks |
| `AI3_MAX_CONCURRENCY_PER_PROVIDER` | 3 | Per-provider limit |
| `AI3_VERIFY` | on | Enable verification |
| `AI3_REPAIR_LIMIT` | 1 | Max repair attempts |

### Model Capabilities

Edit `ai3core/registry/capabilities.json` to:
- Add new models
- Update skill ratings
- Adjust cost/latency estimates
- Enable/disable features

---

## Telemetry & Metrics

### Metrics Collection

The telemetry system tracks:

- **Per-Model Metrics**:
  - Success rate (rolling 24-hour window)
  - Average latency
  - Error rate
  - Total requests
  - Token usage
  - Cost

- **Per-Run Metrics**:
  - Total tasks
  - Parallel tasks executed
  - Total cost
  - Total tokens (input + output)
  - Execution time
  - Verification results

### Using Metrics for Routing

The router uses live telemetry to adjust provider selection:

```python
performance_score = (
    success_rate × 0.7 +
    (1 - normalized_latency) × 0.3
)
```

Models with higher success rates and lower latency are preferred, all else being equal.

---

## Extension Points

### Custom Validators

Add task-specific validation:

```python
def custom_validator(artifact, task):
    # Custom validation logic
    is_valid = check_custom_criteria(artifact)
    confidence = 1.0 if is_valid else 0.5
    return (confidence, is_valid)
```

### Custom Assembly Strategies

Implement new assembly strategies:

```python
def custom_assembly(artifacts: List[Artifact]) -> AssembledResponse:
    # Custom assembly logic
    final_content = merge_logic(artifacts)
    return AssembledResponse(
        content=final_content,
        confidence=calculate_confidence(),
        source_artifacts=[a.id for a in artifacts]
    )
```

---

## Performance Characteristics

### Typical Latencies

- **Planning**: 100-500ms (LLM call to Claude)
- **Routing**: <50ms per task (calculation only)
- **Execution**: 1-5s per task (model-dependent)
- **Verification**: <100ms per artifact
- **Assembly**: <100ms

### Overhead

Total system overhead: ~300-600ms + model latency

### Scalability

- Handles 5-10 concurrent tasks efficiently (default limits)
- Can scale to 50+ tasks with adjusted concurrency settings
- Memory usage scales with artifact size
- Disk usage grows with journal/artifact storage

---

## Future Enhancements

- Multi-modal support (image, audio inputs)
- Advanced assembly strategies (voting, ranked choice)
- Persistent caching layer
- Plugin system for custom extensions
- Web UI dashboard
- Enhanced VS Code integration
- Model fine-tuning based on telemetry

---

## Support & Contributing

For issues or questions:
- Check the [README](README.md) for basic usage
- Review test files in `tests/` for examples
- Examine run traces in `runs/` directory for debugging

**Version**: 2.1
**Last Updated**: 2025-10-20
