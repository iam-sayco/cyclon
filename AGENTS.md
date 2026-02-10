# AGENTS.md - Cyclon AI Assistant Guide

> Quick reference for AI agents working on Cyclon codebase

## Project Overview

**Cyclon** is a TUI-based AI automation tool that orchestrates AI agents to execute coding workflows. Built with Python 3.9+ and Textual framework.

```
Key Stack: Python 3.9+, Textual (TUI), pytest, black, ruff, mypy
Architecture: Layered (UI → Service → Domain → Infrastructure)
```

## Architecture Quick Reference

### Layer Responsibilities

| Layer | Files | Responsibility |
|-------|-------|----------------|
| **UI** | `app.py`, `widgets.py`, `screens.py` | Textual widgets, screens, user interactions |
| **Service** | `services/*.py` | Business logic, no UI dependencies |
| **Domain** | `state.py`, `exceptions.py`, `validation.py`, `constants.py` | Models, validation, state management |
| **Infrastructure** | `paths.py`, `config.py` | File system, external integrations |

### Critical Patterns

1. **Dependency Injection**: Services injected via constructor in `CyclonApp.__init__()`
2. **Observer Pattern**: `AppState` notifies UI observers on state changes
3. **Service Layer**: Business logic lives in services, not in UI

```python
# Good: Service handles business logic
class ConfigService:
    def validate_config(self) -> Tuple[bool, List[str]]: ...

# Bad: Business logic in UI
class CyclonApp:
    def validate_config(self):  # Don't do this
        ...
```

## Code Standards

### Mandatory Checks

```bash
# Run before committing
black .                    # Format (line-length: 100)
ruff check . --fix        # Lint and auto-fix
mypy cyclon/              # Type check (strict mode)
pytest                    # All tests must pass
```

### Style Rules

- **Line length**: 100 characters
- **Type hints**: Python 3.10+ syntax (`str | None`, `list[str]`)
- **Imports**: stdlib → third-party → local (blank lines between)
- **Naming**: snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants
- **Docstrings**: Google format for all public classes/methods

### Prohibited

```python
# Don't use bare except
except:  # ❌ Bad
    pass

except Exception as e:  # ✅ Good
    pass

# Don't use print for debugging
print("debug")  # ❌ Bad

# Don't access UI from services
# Service layer must NOT import from textual
```

## Testing Requirements

### Test Structure

```
tests/
├── unit/                    # Mocked tests (fast, isolated)
│   ├── test_validation.py
│   ├── test_exceptions.py
│   └── services/
│       ├── test_config_service.py
│       ├── test_file_service.py
│       └── test_process_service.py
├── integration/             # Real filesystem tests
│   └── test_services_integration.py
└── conftest.py             # Shared fixtures
```

### Writing Tests

```python
# Unit test - mock external dependencies
def test_load_config_success(config_service, mock_cyclon_paths):
    # Arrange
    mock_config_file.write_text('{"provider": "test"}')

    # Act
    result = config_service.load_config()

    # Assert
    assert result["provider"] == "test"

# Use fixtures from conftest.py
@pytest.fixture
def config_service():
    return ConfigService()
```

### Test Coverage Rules

- **Services**: 90%+ coverage required
- **New features**: Must include tests
- **Edge cases**: Empty inputs, invalid data, exceptions
- **Naming**: `test_<method>_<scenario>_<expected_result>`

### Running Tests

```bash
pytest                              # All tests
pytest tests/unit/test_validation.py # Specific file
pytest -k "config"                  # Pattern match
pytest --cov=cyclon --cov-report=html  # With coverage
```

## Development Workflow

### Adding New Features

1. **Service Layer First**: Implement business logic in appropriate service
2. **Tests**: Write unit tests for new service methods
3. **UI Integration**: Update `CyclonApp` to use service
4. **State**: Use `AppState` for reactive state changes
5. **Docs**: Update relevant documentation

### Example: Adding New Provider

```python
# 1. Add to cyclon/data/providers.json
{
  "new_provider": {
    "label": "New Provider",
    "command": "new-provider run --model {model} --prompt {prompt}"
  }
}

# 2. Test in test_config_service.py
def test_build_command_new_provider():
    ...

# 3. Update ProviderModalScreen if needed (usually automatic)
```

### State Management

```python
# Good: Use AppState with observers
class CyclonApp:
    def _setup_state_observers(self):
        self.app_state.add_process_running_observer(
            lambda old, new: self._update_status(new)
        )

# Good: Update state, UI reacts automatically
self.app_state.process_running = True

# Bad: Direct UI manipulation from services
# Services should never touch UI
```

## Error Handling

### Exception Hierarchy

```
CyclonError (base)
├── ConfigError      # Config file issues
├── FileError        # File operations
├── ProcessError     # Process execution
└── ValidationError  # Input validation
```

### Pattern

```python
# Service layer: Convert infrastructure to domain exceptions
try:
    with open(file_path, 'r') as f:
        return f.read()
except OSError as e:
    raise FileError(f"Cannot read file: {e}")

# UI layer: Catch and display
except FileError as e:
    self.append_output(f"[red]Error: {e}[/red]")
```

## File Locations

```
cyclon/
├── app.py              # Main TUI app - UI coordination only
├── widgets.py          # Custom Textual widgets
├── screens.py          # Modal screens (commands, provider, model, file)
├── state.py            # AppState - centralized state
├── cli.py              # Entry point
├── services/           # Business logic
│   ├── config_service.py
│   ├── file_service.py
│   └── process_service.py
├── data/               # Package data
│   ├── config.json     # Default config
│   ├── providers.json  # Provider definitions
│   └── prompts/        # Prompt templates
└── constants.py        # All constants
```

## Important Decisions

1. **No Repository Pattern**: Services act as repositories (YAGNI)
2. **No Full Command Pattern**: Lightweight command handling (YAGNI)
3. **Python 3.9+ Only**: Use modern syntax
4. **No Backward Compatibility**: This is v2.0.0-rc, clean code only
5. **PTY for Interactive**: Use ptyprocess for interactive commands

## Quick Commands

```bash
# Setup
pip install -e ".[dev]"
pre-commit install

# Development cycle
black . && ruff check . --fix && mypy cyclon/ && pytest

# Run app
python -m cyclon
# or
cyclon
```

## Common Pitfalls

1. **Don't modify business logic in UI**: Move to services
2. **Don't forget tests**: Every public method needs tests
3. **Don't use bare except**: Always catch specific exceptions
4. **Don't hardcode paths**: Use `paths.py` constants
5. **Don't use print**: Use proper logging or UI output methods

## References

- **Architecture**: ARCHITECTURE.md
- **Contributing**: CONTRIBUTING.md
- **User Guide**: README.md
- **Refactoring Plan**: refactoring-tasks.md

---

**Remember**: Write clean, tested, documented code. Follow existing patterns. When in doubt, check existing service implementations.
