# Contributing to Cyclon

Thank you for your interest in contributing to Cyclon! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Style Guide](#style-guide)
- [Naming Conventions](#naming-conventions)
- [How to Write Tests](#how-to-write-tests)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Architecture Guidelines](#architecture-guidelines)
- [Documentation](#documentation)
- [Questions?](#questions)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept constructive criticism gracefully
- Prioritize the community's best interests

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip or pipx

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cyclon.git
   cd cyclon
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/iam-sayco/cyclon.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"
```

This installs:
- All runtime dependencies
- pytest (testing)
- ruff (linting)
- black (formatting)
- mypy (type checking)
- pre-commit (git hooks)

### 3. Install Pre-commit Hooks

```bash
pre-commit install
```

This ensures code quality checks run automatically on every commit.

### 4. Verify Setup

```bash
# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy cyclon/

# Run formatter check
black --check .
```

## Style Guide

We follow PEP 8 with some modifications. Our tools enforce these automatically.

### Python Style (PEP 8 + Black)

- **Line length**: 100 characters maximum
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings, single quotes acceptable for single characters
- **Trailing commas**: Required for multi-line structures

### Black Configuration

Black is configured in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']
```

### Import Order

Use standard library, third-party, local imports with blank lines between:

```python
# Standard library
import json
import os
from pathlib import Path

# Third-party
from textual.app import App
from rich.text import Text

# Local imports
from cyclon.services import ConfigService
from cyclon.exceptions import ConfigError
```

### Type Hints

Use Python 3.10+ syntax for type hints:

```python
# Good
from typing import Optional, List, Dict

def process(data: str | None) -> list[dict[str, Any]]:
    ...

# Avoid (older syntax)
def process(data: Optional[str]) -> List[Dict[str, Any]]:
    ...
```

### Ruff Rules

We use these ruff rules (configured in `pyproject.toml`):

- **E, W**: pycodestyle errors and warnings
- **F**: Pyflakes
- **I**: isort (import sorting)
- **N**: PEP 8 naming conventions
- **D**: pydocstyle (docstrings)
- **UP**: pyupgrade (Python upgrade checks)
- **B**: flake8-bugbear
- **C4**: flake8-comprehensions
- **SIM**: flake8-simplify
- **PL**: Pylint

## Naming Conventions

### General

- **Modules**: `snake_case.py` (e.g., `config_service.py`)
- **Classes**: `PascalCase` (e.g., `ConfigService`)
- **Functions**: `snake_case` (e.g., `validate_config`)
- **Variables**: `snake_case` (e.g., `config_data`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `CONFIG_FILENAME`)
- **Private**: Prefix with underscore (e.g., `_internal_method`)

### Services

Service classes should end with `Service`:

```python
class ConfigService:
    """Service for configuration operations."""
    ...

class FileService:
    """Service for file operations."""
    ...
```

### Exceptions

Exception classes should end with `Error` and inherit from `CyclonError`:

```python
class CyclonError(Exception):
    """Base exception."""
    pass

class ConfigError(CyclonError):
    """Configuration error."""
    pass
```

### Tests

Test functions should start with `test_`:

```python
def test_validate_config_success():
    """Test successful configuration validation."""
    ...

def test_validate_config_missing_provider():
    """Test validation with missing provider."""
    ...
```

## How to Write Tests

### Test Structure

```
tests/
├── unit/              # Unit tests (mocked)
│   ├── test_validation.py
│   ├── test_exceptions.py
│   ├── test_constants.py
│   └── services/
│       ├── test_config_service.py
│       ├── test_file_service.py
│       └── test_process_service.py
├── integration/       # Integration tests
│   └── test_services_integration.py
└── conftest.py        # Shared fixtures
```

### Writing Unit Tests

Unit tests should be fast and isolated. Mock all external dependencies:

```python
import pytest
from unittest.mock import Mock, patch
from cyclon.services import ConfigService

class TestConfigService:
    """Tests for ConfigService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ConfigService()
    
    def test_validate_config_success(self, tmp_path):
        """Test successful config validation."""
        # Arrange
        config_file = tmp_path / "config.json"
        config_file.write_text('{"provider": "test", "model": "gpt-4"}')
        
        with patch('cyclon.services.config_service.LOCAL_CONFIG_FILE', config_file):
            # Act
            is_valid, missing = self.service.validate_config()
            
            # Assert
            assert is_valid is True
            assert missing == []
    
    def test_validate_config_missing_provider(self, tmp_path):
        """Test validation with missing provider."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"model": "gpt-4"}')
        
        with patch('cyclon.services.config_service.LOCAL_CONFIG_FILE', config_file):
            is_valid, missing = self.service.validate_config()
            
            assert is_valid is False
            assert "provider" in missing
```

### Test Naming

- **Descriptive names**: `test_<method>_<scenario>_<expected_result>`
- **Docstrings**: Describe what is being tested
- **Arrange-Act-Assert**: Structure tests clearly

### Fixtures

Use fixtures from `conftest.py` for common setup:

```python
# In conftest.py
import pytest
from cyclon.services import ConfigService, FileService

@pytest.fixture
def config_service():
    """Create ConfigService instance."""
    return ConfigService()

@pytest.fixture
def file_service():
    """Create FileService instance."""
    return FileService()

# In test file
def test_something(config_service):
    """Use fixture directly."""
    result = config_service.validate_config()
    ...
```

### Mocking

Mock external dependencies:

```python
from unittest.mock import Mock, patch, MagicMock

# Mock file operations
with patch('pathlib.Path.exists', return_value=True):
    with patch('builtins.open', mock_open(read_data='{}')):
        result = service.load_config()

# Mock services
mock_config = Mock()
mock_config.validate_config.return_value = (True, [])
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cyclon --cov-report=html

# Run specific test file
pytest tests/unit/test_validation.py

# Run specific test
pytest tests/unit/test_validation.py::test_validate_string_success

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

### Test Coverage

Aim for high coverage, especially for services:

- **Unit tests**: 90%+ coverage
- **Integration tests**: Happy path and error cases
- **Edge cases**: Empty inputs, invalid data, exceptions

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear commit history.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, etc.

### Examples

```
feat(config): add provider validation

Add validation to ensure provider exists in providers.json
before saving configuration. This prevents invalid provider
names from being saved.

Closes #123
```

```
fix(file-service): handle missing plan file

Fix FileError when plan.md doesn't exist during execution.
Now returns None instead of raising exception.
```

```
docs(readme): update installation instructions

Add instructions for pipx installation and virtual
environment setup.
```

```
test(config-service): add tests for edge cases

Add tests for empty config, invalid JSON, and missing
required fields.
```

### Commit Best Practices

1. **Atomic commits**: One logical change per commit
2. **Clear messages**: Explain WHY, not just WHAT
3. **Reference issues**: Use "Closes #123" or "Refs #123"
4. **Keep scope small**: Easier to review and revert

## Pull Request Process

### Before Creating PR

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/2.x
   ```

2. **Run quality checks**:
   ```bash
   # Format code
   black .
   
   # Fix linting
   ruff check . --fix
   
   # Type check
   mypy cyclon/
   
   # Run tests
   pytest
   ```

3. **Update documentation** if needed

4. **Write clear commit messages**

### Creating PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature
   ```

2. **Create PR on GitHub** with:
   - Clear title (conventional commit format)
   - Description of changes
   - Link to related issues
   - Screenshots (if UI changes)

3. **Ensure CI passes**:
   - Tests pass
   - Linting passes
   - Type checking passes

### PR Review Process

1. **Maintainers review** within a few days
2. **Address feedback** promptly
3. **Keep discussions** focused and respectful
4. **Squash commits** if requested
5. **Merge** when approved

## Architecture Guidelines

### Adding New Features

1. **Service Layer**: Add business logic to appropriate service
2. **UI Layer**: Update CyclonApp for UI changes
3. **State**: Use AppState for reactive state
4. **Tests**: Write unit tests for services

### Service Guidelines

Services should:
- Have single responsibility
- Be independent of UI
- Handle their own errors
- Be fully tested

Example:
```python
class NewService:
    """Service for new feature.
    
    This service handles X operations including Y and Z.
    
    Example:
        >>> service = NewService()
        >>> result = service.do_something()
    """
    
    def do_something(self, param: str) -> dict[str, Any]:
        """Do something with param.
        
        Args:
            param: Description of param
            
        Returns:
            Description of return value
            
        Raises:
            ValidationError: If param is invalid
            ServiceError: If operation fails
        """
        # Validate input
        validate_string(param, "param")
        
        try:
            # Business logic
            result = self._process(param)
            return result
        except OSError as e:
            raise ServiceError(f"Operation failed: {e}")
```

### UI Guidelines

CyclonApp should:
- Delegate to services for business logic
- Handle UI state with AppState
- Display user-friendly error messages
- Keep UI code focused on presentation

### State Management

Use AppState for shared state:

```python
# Good: Use AppState
self.app_state.process_running = True

# Good: Use observer pattern
self.app_state.add_process_running_observer(
    lambda old, new: self._update_ui(new)
)
```

### Error Handling

- Services: Raise domain exceptions
- UI: Catch and display errors
- Never swallow exceptions silently

```python
# Service layer
try:
    with open(file_path) as f:
        return f.read()
except OSError as e:
    raise FileError(f"Cannot read file: {e}")

# UI layer
try:
    content = service.load_file()
except FileError as e:
    self.show_error(f"Failed to load: {e}")
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def example(param1: str, param2: int | None = None) -> bool:
    """Short description.
    
    Longer description if needed. Explain what the function does
    and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        FileError: When file operation fails
        
    Example:
        >>> example("test", 42)
        True
    """
```

### README Updates

Update README.md when:
- Adding new commands
- Changing installation process
- Adding new features
- Updating requirements

### Architecture Documentation

Update ARCHITECTURE.md when:
- Adding new services
- Changing architecture
- Adding new patterns
- Changing data flows

## Questions?

If you have questions:

1. **Check documentation**: README, ARCHITECTURE, this file
2. **Search issues**: Maybe already discussed
3. **Ask in discussions**: GitHub Discussions
4. **Create an issue**: For bugs or feature requests

## Resources

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Textual Documentation](https://textual.textualize.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [ruff Documentation](https://docs.astral.sh/ruff/)

## Distribution and Release

### Building Distribution Package

```bash
python -m build
```

This creates:
- `dist/cyclon-*.tar.gz` (source distribution)
- `dist/cyclon-*-py3-none-any.whl` (wheel)

### Uploading to PyPI

```bash
pip install twine
twine upload dist/*
```

### Uninstalling

```bash
# If installed with pip
pip uninstall cyclon

# If installed with pipx
pipx uninstall cyclon

# Clean all files
rm -rf .cyclon  # Remove user configuration
```

## FAQ

**Q: Do dependencies install automatically?**  
A: Yes, pip/pipx reads `pyproject.toml` and installs all dependencies automatically.

**Q: Can I test without installing?**  
A: Yes, run directly with Python: `python -m cyclon` (requires dependencies installed).

**Q: How do I update after code changes?**  
A: With `pip install -e .` - no action needed. With pipx - run `pipx install . --force-reinstall`.

**Q: What's the difference between pip and pipx for development?**  
A: Use `pip install -e .` for development (editable, fast iteration). Use pipx only when testing final distribution.

**Q: Can I use Cyclon without virtual environment?**  
A: Yes, but using a venv is recommended to avoid polluting system packages.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Cyclon! 🚀
