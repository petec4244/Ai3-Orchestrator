import json
from pathlib import Path
from ai3core.settings import REGISTRY_DIR


def load_registry() -> dict:
    """Load provider registry from capabilities.json."""
    registry_file = REGISTRY_DIR / "capabilities.json"
    with open(registry_file, "r") as f:
        return json.load(f)
