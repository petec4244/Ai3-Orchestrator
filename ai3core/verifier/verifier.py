"""
Verifier - Validates output quality against success criteria
"""

import re
from typing import List, Dict, Optional, Callable
from ..types import ExecutionArtifact, VerificationResult, Task


class Verifier:
    """
    Quality verification engine

    Checks artifacts against:
    - Explicit success criteria from task
    - General quality heuristics
    - Custom validation rules

    Can trigger:
    - Repair subtasks
    - Fallback to different model
    - Human review escalation
    """

    # Minimum response length to be considered valid
    MIN_RESPONSE_LENGTH = 10

    # Quality score thresholds
    PASS_THRESHOLD = 0.7
    REPAIR_THRESHOLD = 0.5

    def __init__(self, custom_validators: Optional[Dict[str, Callable]] = None):
        """
        Initialize the verifier

        Args:
            custom_validators: Optional dict of task_type -> validation function
        """
        self.custom_validators = custom_validators or {}

    def verify(self, artifact: ExecutionArtifact, task: Task) -> VerificationResult:
        """
        Verify an artifact against task requirements

        Args:
            artifact: Execution artifact to verify
            task: Original task with success criteria

        Returns:
            VerificationResult with pass/fail and feedback
        """
        # Check if execution succeeded
        if not artifact.success:
            return VerificationResult(
                artifact_id=f"{artifact.task_id}:{artifact.model_id}",
                passed=False,
                score=0.0,
                criteria_results={},
                feedback=f"Execution failed: {artifact.error}",
                needs_repair=True,
                suggested_fixes=["Retry with different model", "Check input parameters"]
            )

        # Run validation checks
        criteria_results = {}
        scores = []

        # 1. Check basic quality
        basic_score, basic_result = self._check_basic_quality(artifact)
        criteria_results["basic_quality"] = basic_result
        scores.append(basic_score)

        # 2. Check against explicit success criteria
        for criterion in task.success_criteria:
            score, result = self._check_criterion(artifact, criterion)
            criteria_results[criterion] = result
            scores.append(score)

        # 3. Run task-type specific validation
        if task.task_type in self.custom_validators:
            custom_score, custom_result = self.custom_validators[task.task_type](artifact, task)
            criteria_results["custom_validation"] = custom_result
            scores.append(custom_score)

        # 4. Check for common failure patterns
        failure_score, failure_result = self._check_failure_patterns(artifact)
        criteria_results["failure_patterns"] = failure_result
        scores.append(failure_score)

        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0

        # Determine pass/fail
        passed = overall_score >= self.PASS_THRESHOLD
        needs_repair = overall_score < self.REPAIR_THRESHOLD

        # Generate feedback
        feedback = self._generate_feedback(criteria_results, overall_score)

        # Suggest fixes if needed
        suggested_fixes = []
        if not passed:
            suggested_fixes = self._suggest_fixes(artifact, task, criteria_results)

        return VerificationResult(
            artifact_id=f"{artifact.task_id}:{artifact.model_id}",
            passed=passed,
            score=overall_score,
            criteria_results=criteria_results,
            feedback=feedback,
            needs_repair=needs_repair,
            suggested_fixes=suggested_fixes
        )

    def _check_basic_quality(self, artifact: ExecutionArtifact) -> tuple:
        """
        Check basic response quality

        Returns:
            (score, passed) tuple
        """
        response = artifact.response.strip()

        # Check minimum length
        if len(response) < self.MIN_RESPONSE_LENGTH:
            return 0.0, False

        # Check for empty/placeholder responses
        placeholder_patterns = [
            r"^(todo|tbd|coming soon|not implemented)$",
            r"^(\.\.\.|…)$",
            r"^(error|failed|unable)$"
        ]

        for pattern in placeholder_patterns:
            if re.match(pattern, response.lower()):
                return 0.2, False

        # Check token efficiency (not too short for the latency)
        output_tokens = artifact.token_usage.get("output", 0)
        if output_tokens < 10:
            return 0.5, False

        return 1.0, True

    def _check_criterion(self, artifact: ExecutionArtifact, criterion: str) -> tuple:
        """
        Check a specific success criterion

        Returns:
            (score, passed) tuple
        """
        response = artifact.response.lower()
        criterion_lower = criterion.lower()

        # Simple keyword matching for now
        # Can be enhanced with semantic similarity

        # Check for explicit success phrases
        if any(phrase in criterion_lower for phrase in ["complete", "success", "valid"]):
            # Look for completion indicators
            if any(indicator in response for indicator in ["done", "completed", "successfully", "finished"]):
                return 1.0, True

        # Check for specific requirements
        if "test" in criterion_lower or "verify" in criterion_lower:
            # Look for validation evidence
            if any(word in response for word in ["tested", "verified", "validated", "passed"]):
                return 1.0, True
            return 0.5, False

        if "error" in criterion_lower or "bug" in criterion_lower or "fix" in criterion_lower:
            # Look for resolution evidence
            if any(word in response for word in ["fixed", "resolved", "corrected", "solved"]):
                return 1.0, True
            return 0.5, False

        # Default: assume criterion is met if response is substantial
        if len(artifact.response) > 100:
            return 0.8, True

        return 0.6, True

    def _check_failure_patterns(self, artifact: ExecutionArtifact) -> tuple:
        """
        Check for common failure patterns in response

        Returns:
            (score, passed) tuple
        """
        response = artifact.response.lower()

        failure_patterns = [
            "i cannot",
            "i can't",
            "unable to",
            "don't have access",
            "not possible",
            "error occurred",
            "failed to",
            "couldn't",
            "insufficient information",
            "apologize"
        ]

        # Count failure indicators
        failure_count = sum(1 for pattern in failure_patterns if pattern in response)

        if failure_count >= 3:
            return 0.0, False
        elif failure_count >= 1:
            return 0.5, False

        return 1.0, True

    def _generate_feedback(self, criteria_results: Dict[str, bool], score: float) -> str:
        """Generate human-readable feedback"""
        passed_criteria = [k for k, v in criteria_results.items() if v]
        failed_criteria = [k for k, v in criteria_results.items() if not v]

        parts = [f"Quality Score: {score:.2f} / 1.0"]

        if passed_criteria:
            parts.append(f"Passed: {', '.join(passed_criteria)}")

        if failed_criteria:
            parts.append(f"Failed: {', '.join(failed_criteria)}")

        if score >= self.PASS_THRESHOLD:
            parts.append("Status: PASSED ✓")
        elif score >= self.REPAIR_THRESHOLD:
            parts.append("Status: NEEDS IMPROVEMENT")
        else:
            parts.append("Status: FAILED - REPAIR NEEDED")

        return " | ".join(parts)

    def _suggest_fixes(self, artifact: ExecutionArtifact, task: Task,
                      criteria_results: Dict[str, bool]) -> List[str]:
        """Suggest fixes for failed verification"""
        fixes = []

        # Check what failed
        if not criteria_results.get("basic_quality", True):
            fixes.append("Response is too short or low quality - retry with more specific prompt")

        if not criteria_results.get("failure_patterns", True):
            fixes.append("Response contains failure indicators - try different model")

        # Check for specific failed criteria
        failed = [k for k, v in criteria_results.items() if not v and k not in ["basic_quality", "failure_patterns"]]

        if failed:
            fixes.append(f"Explicitly address these criteria: {', '.join(failed)}")

        # Model-specific suggestions
        if artifact.error_rate and artifact.error_rate > 0.1:
            fixes.append(f"Model {artifact.model_id} has high error rate - consider alternative")

        # Generic suggestions
        if not fixes:
            fixes = [
                "Refine prompt with more specific instructions",
                "Try a different model with higher skill rating",
                "Add more context to the task"
            ]

        return fixes

    def batch_verify(self, artifacts: List[ExecutionArtifact],
                    tasks: Dict[str, Task]) -> Dict[str, VerificationResult]:
        """
        Verify multiple artifacts

        Args:
            artifacts: List of artifacts to verify
            tasks: Dict mapping task_id -> Task

        Returns:
            Dict mapping artifact_id -> VerificationResult
        """
        results = {}

        for artifact in artifacts:
            task = tasks.get(artifact.task_id)
            if not task:
                continue

            result = self.verify(artifact, task)
            results[result.artifact_id] = result

        return results

    def get_repair_tasks(self, verification: VerificationResult,
                        original_task: Task) -> List[Task]:
        """
        Generate repair subtasks based on verification failure

        Args:
            verification: Failed verification result
            original_task: The original task

        Returns:
            List of repair tasks
        """
        if verification.passed:
            return []

        # Create repair task
        repair_description = f"Repair failed task: {original_task.description}\n"
        repair_description += f"Issues: {verification.feedback}\n"
        repair_description += f"Suggested fixes: {', '.join(verification.suggested_fixes)}"

        from uuid import uuid4
        repair_task = Task(
            id=str(uuid4())[:8],
            description=repair_description,
            task_type=original_task.task_type,
            dependencies=[],
            success_criteria=original_task.success_criteria,
            context={
                **original_task.context,
                "is_repair": True,
                "original_task_id": original_task.id,
                "verification_feedback": verification.feedback
            }
        )

        return [repair_task]
