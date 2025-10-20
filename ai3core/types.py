"""
Core type definitions for Ai3Core
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ModelProvider(Enum):
    """Supported AI model providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    XAI = "xai"


@dataclass
class Task:
    """Represents a single task in the plan"""
    id: str
    description: str
    task_type: str  # coding, reasoning, creative, etc.
    dependencies: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_model: Optional[str] = None
    priority: int = 0


@dataclass
class TaskGraph:
    """Directed Acyclic Graph of tasks"""
    tasks: Dict[str, Task]
    root_task_ids: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelCapability:
    """Capabilities and metrics for a specific model"""
    model_id: str
    provider: ModelProvider
    skills: Dict[str, float]  # skill_name -> proficiency (0-1)
    context_window: int
    cost_per_1k_tokens: float
    avg_latency_ms: float
    error_rate: float
    supports_streaming: bool
    supports_vision: bool
    supports_function_calling: bool
    max_output_tokens: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionArtifact:
    """Result artifact from a task execution"""
    task_id: str
    model_id: str
    provider: ModelProvider
    prompt: str
    response: str
    metadata: Dict[str, Any]
    token_usage: Dict[str, int]
    latency_ms: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of quality verification"""
    artifact_id: str
    passed: bool
    score: float  # 0-1
    criteria_results: Dict[str, bool]
    feedback: str
    needs_repair: bool
    suggested_fixes: List[str] = field(default_factory=list)


@dataclass
class AssembledResponse:
    """Final assembled response from multiple artifacts"""
    content: str
    source_artifacts: List[str]
    confidence: float
    assembly_method: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunTrace:
    """Complete execution trace for a run"""
    run_id: str
    original_prompt: str
    plan: TaskGraph
    artifacts: List[ExecutionArtifact]
    verifications: List[VerificationResult]
    final_response: AssembledResponse
    total_cost: float
    total_latency_ms: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
