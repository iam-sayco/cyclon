"""Configuration paths for Cyclon."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

PROVIDERS_FILE = PROJECT_ROOT / "cyclon" / "data" / "providers.json"
DEFAULT_CONFIG_FILE = PROJECT_ROOT / "cyclon" / "data" / "config.json"
LOGO_FILE = PROJECT_ROOT / "cyclon" / "data" / "logo.md"
PROMPTS_DIR = PROJECT_ROOT / "cyclon" / "data" / "prompts"

LOCAL_CYCLON_DIR = Path.cwd() / ".cyclon"
LOCAL_CONFIG_FILE = LOCAL_CYCLON_DIR / "config.json"
LOCAL_PLAN_FILE = LOCAL_CYCLON_DIR / "plan.md"
LOCAL_PROMPT_FILE = LOCAL_CYCLON_DIR / "prompt.md"
LOCAL_LOCK_FILE = LOCAL_CYCLON_DIR / "process.lock"
