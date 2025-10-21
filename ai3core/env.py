"""Environment variable management with .env file support."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# Load .env file from project root (one level up from ai3core)
_project_root = Path(__file__).parent.parent
_env_file = _project_root / ".env"

# Try to load .env file if it exists
if _env_file.exists():
    load_dotenv(_env_file)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable from either system environment or .env file.

    Priority:
    1. System environment variables (export/set commands)
    2. .env file in project root
    3. Default value if provided

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


def require_env(key: str) -> str:
    """
    Get required environment variable, raise error if not found.

    Args:
        key: Environment variable name

    Returns:
        Environment variable value

    Raises:
        ValueError: If environment variable is not set
    """
    value = get_env(key)
    if value is None:
        raise ValueError(
            f"{key} environment variable not set. "
            f"Please set it in your system environment or add it to the .env file at: {_env_file}"
        )
    return value
