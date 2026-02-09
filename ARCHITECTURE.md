# Cyclon Architecture

This document describes the architecture, design patterns, and main operation flows of the Cyclon application.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture Layers](#architecture-layers)
- [Design Patterns](#design-patterns)
- [Main Operation Flows](#main-operation-flows)
- [Component Diagram](#component-diagram)
- [Data Flow](#data-flow)
- [Error Handling](#error-handling)
- [State Management](#state-management)

## Overview

Cyclon is a TUI-based AI automation tool that orchestrates AI agents to execute complex coding workflows. The application follows a layered architecture with clear separation of concerns:

- **UI Layer**: Textual-based widgets and screens
- **Service Layer**: Business logic and domain operations
- **Domain Layer**: Models, exceptions, validation, and constants
- **Infrastructure Layer**: File system and process management

## Project Structure

```
cyclon/
├── cyclon/                 # Main application package
│   ├── __init__.py        # Package exports
│   ├── __main__.py        # Entry point for `python -m cyclon`
│   ├── cli.py             # CLI entry point
│   ├── app.py             # CyclonApp - main TUI application
│   ├── widgets.py         # Textual widgets
│   ├── screens.py         # Modal screens
│   ├── state.py           # AppState - centralized state management
│   ├── config.py          # Configuration manager
│   ├── constants.py       # Application constants
│   ├── paths.py           # File paths configuration
│   ├── exceptions.py      # Custom exceptions
│   ├── validation.py      # Validation utilities
│   ├── services/          # Business logic services
│   │   ├── __init__.py
│   │   ├── config_service.py   # Configuration operations
│   │   ├── file_service.py     # File operations
│   │   └── process_service.py  # Process management with PTY
│   └── data/              # Runtime data
│       ├── config.json    # Default configuration
│       ├── providers.json # Available providers
│       ├── logo.md        # ASCII logo
│       └── prompts/       # Prompt templates
│           ├── execute.md
│           └── generate.md
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
├── pyproject.toml         # Package configuration
├── README.md              # User documentation
├── CONTRIBUTING.md        # Development guidelines
└── ARCHITECTURE.md        # This file
```

## Architecture Layers

### 1. UI Layer (Presentation)

Responsible for user interface and user interactions.

**Components:**
- `CyclonApp` (app.py): Main application class, coordinates UI and business logic
- Widgets (widgets.py): TerminalOutput, StatusIndicator, Throbber, etc.
- Screens (screens.py): Modal screens for commands, provider selection, etc.

**Responsibilities:**
- Render UI components
- Handle user input
- Display output and logs
- Coordinate with services

### 2. Service Layer (Business Logic)

Contains all business logic, decoupled from UI.

**Components:**
- `ConfigService`: Configuration loading, saving, and validation
- `FileService`: File operations and session management
- `ProcessService`: Process execution with PTY support

**Responsibilities:**
- Implement business rules
- Manage configuration
- Handle file operations
- Execute processes

### 3. Domain Layer

Domain models, exceptions, validation rules, and constants.

**Components:**
- `exceptions.py`: Custom exception hierarchy
- `validation.py`: Input validation functions
- `constants.py`: Application constants
- `AppState` (state.py): Centralized state management

**Responsibilities:**
- Define domain concepts
- Enforce business rules
- Provide validation
- Manage application state

### 4. Infrastructure Layer

External systems and technical details.

**Components:**
- `paths.py`: File system paths
- PTY process management
- JSON file I/O

**Responsibilities:**
- File system access
- Process management
- External integrations

## Design Patterns

### 1. Dependency Injection (DI)

Services are injected into CyclonApp constructor, enabling:
- Testability (mock services in tests)
- Loose coupling
- Clear dependencies

```python
class CyclonApp(App):
    def __init__(self, config_service: ConfigService, 
                 file_service: FileService, 
                 process_service: ProcessService):
        # Services injected, not created
```

### 2. Service Layer Pattern

Business logic extracted from UI into dedicated services:
- `ConfigService`: Configuration management
- `FileService`: File operations
- `ProcessService`: Process execution

Each service has a single responsibility (SRP).

### 3. Observer Pattern

`AppState` uses observer pattern for UI updates:
```python
state.add_pty_mode_observer(callback)
state.add_throbber_observer(callback)
state.add_process_running_observer(callback)
```

When state changes, observers are notified automatically.

### 4. Repository Pattern (Implicit)

Services act as repositories for their domains:
- `ConfigService` manages config.json
- `FileService` manages all files in .cyclon/

### 5. Exception Hierarchy

Custom exceptions for different error types:
```
CyclonError (base)
├── ConfigError
├── FileError
├── ProcessError
└── ValidationError
```

## Main Operation Flows

### 1. Application Startup

```
1. CLI (cli.py) creates services
2. Services injected into CyclonApp
3. AppState initialized
4. Textual app starts
5. UI composed (on_mount)
6. Configuration validated
7. Status message displayed
```

### 2. Plan Generation Flow

```
1. User types: /plan <prompt>
2. Input parsed by _parse_command()
3. Command validated (_validate_command_state)
4. FileService.load_generate_prompt() called
5. Prompt template loaded and {user_prompt} replaced
6. ConfigService.build_command() builds provider command
7. ProcessService.run_provider_process() executes
8. Output displayed in terminal
9. Plan saved to .cyclon/plan.md
```

### 3. Plan Execution Flow

```
1. User types: /run
2. Validation checks if plan.md exists
3. FileService.build_execution_prompt() builds full prompt
4. ConfigService.build_command() builds provider command
5. Lock file created (.cyclon/process.lock)
6. ProcessService.run_provider_process() starts
7. Real-time output displayed
8. Exception checking on output
9. On completion: lock file removed
10. Success/failure status displayed
```

### 4. Configuration Flow

```
1. User types: /provider
2. ProviderModalScreen displayed
3. User selects provider
4. ConfigService.save_provider_config() saves
5. Config reloaded and validated
6. Status updated
```

### 5. Session Cleanup Flow

```
1. User types: /new-session
2. Confirmation shown
3. FileService.clear_session() called
4. All files removed except config.json
5. Directories cleaned up
6. UI output cleared
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (Presentation)                 │
├─────────────────────────────────────────────────────────────┤
│  CyclonApp                                                  │
│  ├── Widgets (TerminalOutput, StatusIndicator, etc.)        │
│  ├── Screens (CommandsModal, ProviderModal, etc.)           │
│  └── State observers for UI updates                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer (Business Logic)          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ ConfigService│  │ FileService  │  │ProcessService│       │
│  │              │  │              │  │              │       │
│  │ • validate   │  │ • save_file  │  │ • run_process│       │
│  │ • load/save  │  │ • load_plan  │  │ • stop       │       │
│  │ • build_cmd  │  │ • clear      │  │ • write      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   AppState   │  │  Exceptions  │  │  Validation  │       │
│  │              │  │              │  │              │       │
│  │ • pty_mode   │  │ • ConfigError│  │ • validate_  │       │
│  │ • process    │  │ • FileError  │  │   string     │       │
│  │ • observers  │  │ • etc.       │  │ • etc.       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  Constants: CONFIG_FILENAME, TIMEOUTS, COMMANDS_DATA        │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
├─────────────────────────────────────────────────────────────┤
│  • File System (pathlib)                                    │
│  • PTY Process (ptyprocess)                                 │
│  • JSON I/O                                                 │
│  • Asyncio                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Configuration Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Default    │────▶│   Config     │────▶│   Local     │
│  config     │     │   Service    │     │  config     │
│  (packaged) │     │   (merge)    │     │  (override) │
└─────────────┘     └──────────────┘     └─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   CyclonApp      │
                    │   (validation)   │
                    └──────────────────┘
```

### Execution Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  plan.md    │────▶│   File       │────▶│  Execution  │
│             │     │   Service    │     │   prompt    │
└─────────────┘     │  (template)  │     └──────┬──────┘
                    └──────────────┘              │
┌─────────────┐                                   │
│  prompt.md  │───────────────────────────────────┤
│  (optional) │                                   │
└─────────────┘                                   ▼
                                        ┌──────────────────┐
                                        │ ProcessService   │
                                        │   (PTY exec)     │
                                        └────────┬─────────┘
                                                 │
                    ┌────────────────────────────┼────────────┐
                    ▼                            ▼            ▼
            ┌──────────────┐            ┌──────────────┐ ┌──────────┐
            │   Terminal   │            │     Log      │ │  Status  │
            │   Output     │            │   Output     │ │  Update  │
            └──────────────┘            └──────────────┘ └──────────┘
```

## Error Handling

### Exception Hierarchy

```
Exception
└── CyclonError (base)
    ├── ConfigError
    │   └── Invalid JSON
    │   └── Missing file
    │   └── Invalid configuration
    ├── FileError
    │   └── Read error
    │   └── Write error
    │   └── Permission denied
    ├── ProcessError
    │   └── Process not found
    │   └── Execution failed
    │   └── Timeout
    └── ValidationError
        └── Invalid input
        └── Type error
```

### Error Handling Strategy

1. **Service Layer**: Catches infrastructure exceptions (OSError, JSONDecodeError) and converts to domain exceptions
2. **UI Layer**: Catches domain exceptions and displays user-friendly messages
3. **Validation Layer**: Raises ValidationError for invalid inputs

Example:
```python
# In FileService
try:
    with open(file_path, 'r') as f:
        content = f.read()
except OSError as e:
    raise FileError(f"Error reading file: {e}")

# In CyclonApp
try:
    content = self.file_service.load_content("plan.md")
except FileError as e:
    self.append_output(f"[red]Error: {e}[/red]")
```

## State Management

### AppState Architecture

Centralized state management with observer pattern:

```
┌─────────────────────────────────────┐
│            AppState                 │
├─────────────────────────────────────┤
│  Process State                      │
│  ├── current_process                │
│  ├── current_process_pid            │
│  └── current_pty                    │
│                                     │
│  UI State                           │
│  ├── pty_mode                       │
│  ├── should_stop_processing         │
│  ├── throbber_active                │
│  └── process_running                │
│                                     │
│  Observers                          │
│  ├── _pty_mode_observers[]          │
│  ├── _throbber_observers[]          │
│  └── _process_running_observers[]   │
└─────────────────────────────────────┘
```

### State Flow

1. **State Change**: Property setter called
2. **Validation**: Value validated
3. **Update**: Internal state updated
4. **Notification**: Observers notified (if value changed)
5. **UI Update**: Observers update UI components

Example:
```python
# In AppState
@process_running.setter
def process_running(self, value: bool) -> None:
    if self._process_running != value:
        old_value = self._process_running
        self._process_running = value
        self._notify_process_running_observers(old_value, value)

# In CyclonApp
def _setup_state_observers(self):
    self.app_state.add_process_running_observer(
        lambda old, new: self._update_process_status(new)
    )
```

## Testing Architecture

### Test Structure

```
tests/
├── unit/                    # Unit tests (mocked)
│   ├── test_validation.py   # Validation functions
│   ├── test_exceptions.py   # Exception classes
│   ├── test_constants.py    # Constants
│   └── services/            # Service tests
│       ├── test_config_service.py
│       ├── test_file_service.py
│       └── test_process_service.py
├── integration/             # Integration tests
│   └── test_services_integration.py
└── fixtures/                # Test data
    ├── sample_config.json
    ├── sample_providers.json
    └── sample_plan.md
```

### Testing Approach

- **Unit Tests**: Mock all dependencies, test in isolation
- **Integration Tests**: Test services together
- **Fixtures**: Reusable test data

Example:
```python
# Unit test - mocked
def test_save_file_success(file_service, mock_cyclon_paths):
    file_service.save_file("test.txt", "content")
    # Assert file was created

# Integration test - real filesystem
def test_full_workflow(config_service, file_service):
    # Test actual file operations
```

## Key Decisions

### 1. Why Services?

**Decision**: Extract business logic from CyclonApp into services.

**Rationale**:
- CyclonApp was 871 lines, violating SRP
- Services enable unit testing without Textual
- Clear separation: UI vs Business Logic

**Result**: CyclonApp reduced from 871 to ~630 lines.

### 2. Why Observer Pattern for State?

**Decision**: Use observer pattern in AppState for UI updates.

**Rationale**:
- Avoid direct UI references in state
- Enable multiple UI components to react to state changes
- Testable state management

**Result**: Clean separation between state and UI.

### 3. Why Custom Exceptions?

**Decision**: Create custom exception hierarchy.

**Rationale**:
- Clear error types for different domains
- Consistent error handling across app
- Better testability

**Result**: 5 domain-specific exceptions.

### 4. Why No Repository Pattern?

**Decision**: Services act as repositories, no separate repository layer.

**Rationale**:
- YAGNI - current complexity doesn't warrant extra layer
- Services already abstract file operations
- Adding repositories would add 200+ lines of boilerplate

**Result**: Simpler architecture, easier to understand.

## Future Considerations

### Potential Enhancements

1. **Caching**: Add caching to ConfigService.load_providers() and load_config()
2. **Async/Await**: Review blocking operations for async usage
3. **Plugin System**: Support custom providers via plugins
4. **State Persistence**: Save/restore application state

### Architectural Improvements

1. **Event Bus**: Replace direct callbacks with event bus for looser coupling
2. **Command Pattern**: If command complexity grows, implement full Command pattern
3. **Undo/Redo**: Add undo/redo capability for plan modifications

## References

- [Textual Documentation](https://textual.textualize.io/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Observer Pattern](https://en.wikipedia.org/wiki/Observer_pattern)
