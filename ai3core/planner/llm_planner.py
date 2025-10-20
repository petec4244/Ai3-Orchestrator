import json
import re
from typing import Any, Dict, List
from ai3core.providers.anthropic import AnthropicProvider
from ai3core.settings import AI3_PLANNER_MODEL, AI3_PLANNER_MAXTOK, AI3_PLANNER_TEMPERATURE


PLANNING_PROMPT_TEMPLATE = """You are a task planning agent. Given a user request, decompose it into a directed acyclic graph (DAG) of tasks.

Output ONLY valid JSON matching this schema:
{{
  "tasks": [
    {{
      "id": "t1",
      "type": "generate|transform|synthesize",
      "description": "...",
      "requirements": {{
        "capability": "text-generation|reasoning|...",
        "min_quality": 0.0-1.0
      }},
      "quality_criteria": ["criterion1", "criterion2"]
    }}
  ],
  "edges": [
    {{
      "from": "t1",
      "to": "t2",
      "join": "all|any"
    }}
  ]
}}

User request: {user_input}

Return ONLY the JSON object, no markdown fences, no prose."""


def auto_repair_json(raw: str) -> Dict[str, Any]:
    """Attempt to fix common JSON issues: strip prose, balance brackets, convert JSON5."""
    # Strip markdown code fences
    raw = re.sub(r"```(?:json)?\s*", "", raw)
    raw = raw.strip()

    # Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Extract first { ... } block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Attempt bracket balancing (simple heuristic)
    open_braces = raw.count("{")
    close_braces = raw.count("}")
    if open_braces > close_braces:
        raw += "}" * (open_braces - close_braces)
    elif close_braces > open_braces:
        raw = "{" * (close_braces - open_braces) + raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Last resort: strip trailing commas (JSON5 compatibility)
        raw = re.sub(r",\s*([\]}])", r"\1", raw)
        return json.loads(raw)


def validate_task_graph(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize TaskGraph structure."""
    if "tasks" not in data or not isinstance(data["tasks"], list):
        raise ValueError("Missing or invalid 'tasks' field")

    if "edges" not in data:
        data["edges"] = []

    # Validate task IDs are unique
    task_ids = {t.get("id") for t in data["tasks"]}
    if len(task_ids) != len(data["tasks"]):
        raise ValueError("Duplicate task IDs detected")

    # Validate edges reference existing tasks
    for edge in data["edges"]:
        if edge.get("from") not in task_ids or edge.get("to") not in task_ids:
            raise ValueError(f"Edge references non-existent task: {edge}")
        if "join" not in edge:
            edge["join"] = "all"

    # Set defaults for tasks
    for task in data["tasks"]:
        if "type" not in task:
            task["type"] = "generate"
        if "requirements" not in task:
            task["requirements"] = {"capability": "text-generation", "min_quality": 0.7}
        if "quality_criteria" not in task:
            task["quality_criteria"] = []

    return data


async def make_plan(user_input: str) -> Dict[str, Any]:
    """Generate a TaskGraph using LLM planner with auto-repair."""
    provider = AnthropicProvider(
        model=AI3_PLANNER_MODEL,
        max_tokens=AI3_PLANNER_MAXTOK,
        temperature=AI3_PLANNER_TEMPERATURE
    )

    prompt = PLANNING_PROMPT_TEMPLATE.format(user_input=user_input)

    response = await provider.generate(prompt)
    raw_output = response.get("content", "")

    # Attempt auto-repair
    try:
        data = auto_repair_json(raw_output)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse planner output: {e}\nRaw: {raw_output}")

    # Validate and normalize
    return validate_task_graph(data)
