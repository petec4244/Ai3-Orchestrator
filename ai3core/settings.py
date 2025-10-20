import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
REGISTRY_DIR = BASE_DIR / "ai3core" / "registry"
JOURNAL_DIR = BASE_DIR / "runs"
TELEMETRY_DIR = BASE_DIR / "telemetry"

# Ensure directories exist
JOURNAL_DIR.mkdir(exist_ok=True)
TELEMETRY_DIR.mkdir(exist_ok=True)

# LLM Planner settings
AI3_PLANNER_MODEL = os.getenv("AI3_PLANNER_MODEL", "claude-3-7-sonnet-latest")
AI3_PLANNER_MAXTOK = int(os.getenv("AI3_PLANNER_MAXTOK", "4096"))
AI3_PLANNER_TEMPERATURE = float(os.getenv("AI3_PLANNER_TEMPERATURE", "0.0"))

# Executor settings
AI3_MAX_CONCURRENCY = int(os.getenv("AI3_MAX_CONCURRENCY", "5"))
AI3_MAX_CONCURRENCY_PER_PROVIDER = int(os.getenv("AI3_MAX_CONCURRENCY_PER_PROVIDER", "3"))

# Verifier settings
AI3_VERIFY = os.getenv("AI3_VERIFY", "on").lower() in ("on", "true", "1", "yes")
AI3_REPAIR_LIMIT = int(os.getenv("AI3_REPAIR_LIMIT", "1"))

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
