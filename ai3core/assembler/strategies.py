from typing import List, Dict


def assemble_artifacts(artifacts: List[Dict], strategy: str = "concatenate") -> str:
    """Assemble multiple artifacts into final output."""
    if strategy == "concatenate":
        return "\n\n".join(a.get("content", "") for a in artifacts if a.get("content"))

    elif strategy == "merge":
        # Simple merge: join with separators
        parts = []
        for idx, artifact in enumerate(artifacts):
            content = artifact.get("content", "")
            if content:
                parts.append(f"--- Part {idx + 1} ---\n{content}")
        return "\n\n".join(parts)

    elif strategy == "best":
        # Pick artifact with highest quality (by length heuristic)
        best = max(artifacts, key=lambda a: len(a.get("content", "")), default={})
        return best.get("content", "")

    else:
        return "\n\n".join(a.get("content", "") for a in artifacts if a.get("content"))
