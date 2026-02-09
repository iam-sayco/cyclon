"""Pytest configuration and fixtures for Cyclon tests."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio


def pytest_configure(config):
    """Configure pytest before test collection - setup mocked paths."""
    # Remove any cyclon modules that might be already imported
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('cyclon')]
    for mod in modules_to_remove:
        del sys.modules[mod]
    
    # Create a mock paths module
    import types
    mock_paths = types.ModuleType('cyclon.paths')
    
    # Create temp directories
    import tempfile
    base_temp = Path(tempfile.mkdtemp(prefix='cyclon_test_'))
    
    cyclon_dir = base_temp / ".cyclon"
    data_dir = base_temp / "data"
    prompts_dir = data_dir / "prompts"
    
    cyclon_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    prompts_dir.mkdir(exist_ok=True)
    
    # Create required data files
    (data_dir / "providers.json").write_text(json.dumps({}, indent=2))
    (data_dir / "config.json").write_text(json.dumps({}, indent=2))
    (data_dir / "logo.md").write_text("CYCLON")
    (prompts_dir / "execute.md").write_text(
        "CWD: {cwd}\nPlan: {plan_path}\nLock: {lock_file}\nContext: {context_file}\nInstructions: {user_instructions}"
    )
    
    # Set attributes on mock module
    mock_paths.PROJECT_ROOT = base_temp
    mock_paths.PROVIDERS_FILE = data_dir / "providers.json"
    mock_paths.DEFAULT_CONFIG_FILE = data_dir / "config.json"
    mock_paths.LOGO_FILE = data_dir / "logo.md"
    mock_paths.PROMPTS_DIR = prompts_dir
    mock_paths.LOCAL_CYCLON_DIR = cyclon_dir
    mock_paths.LOCAL_CONFIG_FILE = cyclon_dir / "config.json"
    mock_paths.LOCAL_PLAN_FILE = cyclon_dir / "plan.md"
    mock_paths.LOCAL_PROMPT_FILE = cyclon_dir / "prompt.md"
    mock_paths.LOCAL_LOCK_FILE = cyclon_dir / "process.lock"
    
    # Store for cleanup
    pytest_configure.base_temp = base_temp
    
    # Inject into sys.modules BEFORE importing any cyclon modules
    sys.modules['cyclon.paths'] = mock_paths


def pytest_unconfigure(config):
    """Cleanup after all tests."""
    # Cleanup temp directory
    import shutil
    if hasattr(pytest_configure, 'base_temp'):
        shutil.rmtree(pytest_configure.base_temp, ignore_errors=True)


@pytest.fixture
def sample_providers_data():
    """Return sample providers configuration data."""
    return {
        "opencode": {
            "name": "OpenCode",
            "command": "opencode",
            "model_placeholder": "{model}",
            "description": "OpenCode CLI provider"
        },
        "test-provider": {
            "name": "Test Provider",
            "command": ["test", "--model", "{model}", "--prompt", "{prompt}"],
            "model_placeholder": "{model}",
            "description": "Test provider for unit tests"
        },
        "complex-provider": {
            "name": "Complex Provider",
            "command": ["complex", "--provider", "{model}", "--input", "{prompt}"],
            "model_placeholder": "{model}",
            "description": "Provider with different placeholders"
        }
    }


@pytest.fixture
def sample_config_data():
    """Return sample configuration data."""
    return {
        "provider": "opencode",
        "model": "gpt-4"
    }


@pytest.fixture
def mock_pty_process():
    """Create a mock PTY process for testing."""
    mock_process = MagicMock()
    mock_process.isalive.return_value = True
    mock_process.pid = 12345
    mock_process.fd = 1
    mock_process.read.return_value = "mock output"
    mock_process.wait.return_value = 0
    return mock_process


@pytest.fixture
def mock_cyclon_paths():
    """Return the mocked paths used by cyclon modules."""
    import cyclon.paths as paths
    return {
        "base_temp": paths.PROJECT_ROOT,
        "cyclon_dir": paths.LOCAL_CYCLON_DIR,
        "data_dir": paths.PROJECT_ROOT / "data",
        "prompts_dir": paths.PROMPTS_DIR,
        "providers_file": paths.PROVIDERS_FILE,
        "default_config_file": paths.DEFAULT_CONFIG_FILE,
        "logo_file": paths.LOGO_FILE,
        "local_config_file": paths.LOCAL_CONFIG_FILE,
        "local_plan_file": paths.LOCAL_PLAN_FILE,
        "local_prompt_file": paths.LOCAL_PROMPT_FILE,
        "local_lock_file": paths.LOCAL_LOCK_FILE,
    }


@pytest.fixture
def config_service(mock_cyclon_paths):
    """Create a ConfigService instance with clean state."""
    from cyclon.services.config_service import ConfigService
    
    # Clean up any existing config files before creating service
    if mock_cyclon_paths["local_config_file"].exists():
        mock_cyclon_paths["local_config_file"].write_text("{}")
    if mock_cyclon_paths["default_config_file"].exists():
        mock_cyclon_paths["default_config_file"].write_text("{}")
    
    return ConfigService()


@pytest.fixture
def file_service():
    """Create a FileService instance."""
    from cyclon.services.file_service import FileService
    return FileService()


@pytest.fixture
def process_service():
    """Create a ProcessService instance."""
    from cyclon.services.process_service import ProcessService
    return ProcessService()


@pytest.fixture
def auto_await_mode(request):
    """Auto-await mode fixture for async tests to prevent infinite loops."""
    import asyncio
    import select

    original_to_thread = asyncio.to_thread
    original_select = select.select

    async def quick_await(*args, **kwargs):
        raise EOFError()  # Force loop to exit

    def patch_to_thread(func, *args, **kwargs):
        return quick_await(func, *args, **kwargs)

    def patch_select(rlist, wlist, xlist, timeout=None):
        # Immediately return empty to prevent blocking
        return ([], [], [])

    asyncio.to_thread = patch_to_thread
    select.select = patch_select

    yield

    asyncio.to_thread = original_to_thread
    select.select = original_select
