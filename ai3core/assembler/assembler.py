"""
Assembler - Combines multiple artifacts into coherent final response
"""

import re
from typing import List, Dict, Optional
from ..types import ExecutionArtifact, AssembledResponse, Task, VerificationResult


class Assembler:
    """
    Assembles multiple task artifacts into a single coherent response

    Handles:
    - Deduplication of redundant content
    - Conflict resolution between contradictory outputs
    - Source attribution and citations
    - Formatting and presentation
    - Confidence scoring
    """

    # Assembly strategies
    STRATEGY_CONCATENATE = "concatenate"         # Simple concatenation
    STRATEGY_SYNTHESIZE = "synthesize"           # Merge and deduplicate
    STRATEGY_BEST_SINGLE = "best_single"         # Pick best artifact
    STRATEGY_CONSENSUS = "consensus"             # Merge common elements

    def __init__(self, default_strategy: str = STRATEGY_SYNTHESIZE):
        """
        Initialize the assembler

        Args:
            default_strategy: Default assembly strategy
        """
        self.default_strategy = default_strategy

    def assemble(self, artifacts: List[ExecutionArtifact],
                tasks: Dict[str, Task],
                verifications: Optional[Dict[str, VerificationResult]] = None,
                strategy: Optional[str] = None) -> AssembledResponse:
        """
        Assemble artifacts into final response

        Args:
            artifacts: List of execution artifacts
            tasks: Dict mapping task_id -> Task
            verifications: Optional verification results
            strategy: Optional override for assembly strategy

        Returns:
            AssembledResponse with assembled content
        """
        strategy = strategy or self.default_strategy

        # Filter out failed artifacts
        successful = [a for a in artifacts if a.success]

        if not successful:
            return self._create_error_response(artifacts)

        # Filter by verification if available
        if verifications:
            verified = [
                a for a in successful
                if verifications.get(f"{a.task_id}:{a.model_id}", None)
                and verifications[f"{a.task_id}:{a.model_id}"].passed
            ]
            if verified:
                successful = verified

        # Apply assembly strategy
        if strategy == self.STRATEGY_CONCATENATE:
            return self._assemble_concatenate(successful, tasks)
        elif strategy == self.STRATEGY_BEST_SINGLE:
            return self._assemble_best_single(successful, tasks, verifications)
        elif strategy == self.STRATEGY_CONSENSUS:
            return self._assemble_consensus(successful, tasks)
        else:  # STRATEGY_SYNTHESIZE
            return self._assemble_synthesize(successful, tasks, verifications)

    def _assemble_concatenate(self, artifacts: List[ExecutionArtifact],
                             tasks: Dict[str, Task]) -> AssembledResponse:
        """Simple concatenation of all responses"""
        parts = []

        for artifact in artifacts:
            task = tasks.get(artifact.task_id)
            task_desc = task.description if task else artifact.task_id

            # Add section header
            parts.append(f"## Task: {task_desc}")
            parts.append(f"*[Processed by {artifact.model_id}]*\n")
            parts.append(artifact.response)
            parts.append("\n" + "="*80 + "\n")

        content = "\n".join(parts)

        return AssembledResponse(
            content=content,
            source_artifacts=[f"{a.task_id}:{a.model_id}" for a in artifacts],
            confidence=0.8,
            assembly_method=self.STRATEGY_CONCATENATE,
            metadata={
                "num_artifacts": len(artifacts),
                "models_used": list(set(a.model_id for a in artifacts))
            }
        )

    def _assemble_best_single(self, artifacts: List[ExecutionArtifact],
                             tasks: Dict[str, Task],
                             verifications: Optional[Dict[str, VerificationResult]]) -> AssembledResponse:
        """Pick the single best artifact"""

        # Score each artifact
        scores = []
        for artifact in artifacts:
            score = self._score_artifact(artifact, verifications)
            scores.append((artifact, score))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        # Take best
        best_artifact, best_score = scores[0]

        task = tasks.get(best_artifact.task_id)
        task_desc = task.description if task else best_artifact.task_id

        content = f"*[Best response from {best_artifact.model_id}]*\n\n{best_artifact.response}"

        return AssembledResponse(
            content=content,
            source_artifacts=[f"{best_artifact.task_id}:{best_artifact.model_id}"],
            confidence=best_score,
            assembly_method=self.STRATEGY_BEST_SINGLE,
            metadata={
                "selected_model": best_artifact.model_id,
                "score": best_score,
                "alternatives": len(artifacts) - 1
            }
        )

    def _assemble_synthesize(self, artifacts: List[ExecutionArtifact],
                            tasks: Dict[str, Task],
                            verifications: Optional[Dict[str, VerificationResult]]) -> AssembledResponse:
        """Synthesize artifacts with deduplication and merging"""

        if len(artifacts) == 1:
            # Single artifact - return as is
            artifact = artifacts[0]
            return AssembledResponse(
                content=artifact.response,
                source_artifacts=[f"{artifact.task_id}:{artifact.model_id}"],
                confidence=self._score_artifact(artifact, verifications),
                assembly_method=self.STRATEGY_SYNTHESIZE,
                metadata={"num_artifacts": 1}
            )

        # Group artifacts by task
        by_task: Dict[str, List[ExecutionArtifact]] = {}
        for artifact in artifacts:
            if artifact.task_id not in by_task:
                by_task[artifact.task_id] = []
            by_task[artifact.task_id].append(artifact)

        # Assemble each task group
        parts = []
        all_sources = []

        for task_id, task_artifacts in by_task.items():
            task = tasks.get(task_id)

            if len(task_artifacts) == 1:
                # Single response for this task
                artifact = task_artifacts[0]
                if task:
                    parts.append(f"### {task.description}\n")
                parts.append(artifact.response)
                all_sources.append(f"{artifact.task_id}:{artifact.model_id}")
            else:
                # Multiple responses - pick best or merge
                best = self._pick_best_artifact(task_artifacts, verifications)
                if task:
                    parts.append(f"### {task.description}\n")
                parts.append(best.response)
                parts.append(f"\n*[Synthesized from {len(task_artifacts)} responses]*")
                all_sources.extend([f"{a.task_id}:{a.model_id}" for a in task_artifacts])

            parts.append("")  # Blank line between sections

        content = "\n".join(parts)

        # Calculate average confidence
        avg_confidence = sum(self._score_artifact(a, verifications) for a in artifacts) / len(artifacts)

        return AssembledResponse(
            content=content,
            source_artifacts=all_sources,
            confidence=avg_confidence,
            assembly_method=self.STRATEGY_SYNTHESIZE,
            metadata={
                "num_tasks": len(by_task),
                "num_artifacts": len(artifacts),
                "models_used": list(set(a.model_id for a in artifacts))
            }
        )

    def _assemble_consensus(self, artifacts: List[ExecutionArtifact],
                           tasks: Dict[str, Task]) -> AssembledResponse:
        """Find consensus among multiple artifacts"""

        # For now, similar to synthesize but could add voting logic
        # This is a placeholder for more sophisticated consensus algorithms

        return self._assemble_synthesize(artifacts, tasks, None)

    def _create_error_response(self, artifacts: List[ExecutionArtifact]) -> AssembledResponse:
        """Create response when all artifacts failed"""

        errors = []
        for artifact in artifacts:
            errors.append(f"- {artifact.model_id}: {artifact.error}")

        content = "All tasks failed:\n" + "\n".join(errors)

        return AssembledResponse(
            content=content,
            source_artifacts=[],
            confidence=0.0,
            assembly_method="error",
            metadata={"all_failed": True}
        )

    def _score_artifact(self, artifact: ExecutionArtifact,
                       verifications: Optional[Dict[str, VerificationResult]]) -> float:
        """Score an artifact for quality"""

        # Base score
        score = 0.7

        # Check verification
        if verifications:
            artifact_id = f"{artifact.task_id}:{artifact.model_id}"
            verification = verifications.get(artifact_id)
            if verification:
                score = verification.score

        # Adjust for token efficiency
        output_tokens = artifact.token_usage.get("output", 0)
        if output_tokens > 100:
            score += 0.1
        if output_tokens > 500:
            score += 0.1

        # Adjust for latency (prefer faster)
        if artifact.latency_ms < 2000:
            score += 0.05

        # Cap at 1.0
        return min(score, 1.0)

    def _pick_best_artifact(self, artifacts: List[ExecutionArtifact],
                           verifications: Optional[Dict[str, VerificationResult]]) -> ExecutionArtifact:
        """Pick the best artifact from a list"""

        scored = [(a, self._score_artifact(a, verifications)) for a in artifacts]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]

    def create_citation_map(self, artifacts: List[ExecutionArtifact],
                           tasks: Dict[str, Task]) -> Dict[str, str]:
        """
        Create a citation map for source attribution

        Returns:
            Dict mapping citation_id -> source description
        """
        citations = {}

        for idx, artifact in enumerate(artifacts, 1):
            task = tasks.get(artifact.task_id)
            task_desc = task.description[:50] if task else artifact.task_id

            citation_id = f"[{idx}]"
            citation_text = f"{artifact.model_id}: {task_desc}... (tokens: {artifact.token_usage.get('total', 0)})"

            citations[citation_id] = citation_text

        return citations

    def format_with_citations(self, response: AssembledResponse,
                             artifacts: List[ExecutionArtifact],
                             tasks: Dict[str, Task]) -> str:
        """
        Format response with citation markers

        Returns:
            Formatted content with citations appended
        """
        citations = self.create_citation_map(artifacts, tasks)

        content_parts = [response.content, "", "---", "", "**Sources:**"]

        for cit_id, cit_text in citations.items():
            content_parts.append(f"{cit_id} {cit_text}")

        return "\n".join(content_parts)
