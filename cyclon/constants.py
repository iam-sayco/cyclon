"""Constants for Cyclon."""

from textual_autocomplete._autocomplete import DropdownItem
from textual.content import Content

# Filenames
CONFIG_FILENAME = "config.json"
PLAN_FILENAME = "plan.md"
PROMPT_FILENAME = "prompt.md"
LOCK_FILENAME = "process.lock"
CONTEXT_FILENAME = "context.md"

# Timeouts and delays (in seconds)
PLAN_GENERATION_TIMEOUT = 600
EXECUTION_TIMEOUT = 3600
EXCEPTION_RETRY_DELAY = 10
PROCESS_TERMINATION_DELAY = 0.1

# UI constants
LOG_MAX_LINES = 10000

# Commands
COMMANDS_DATA = [
    ("/plan", "View/edit plan or generate new with prompt"),
    ("/run", "Execute the plan"),
    ("/stop", "Stop current process"),
    ("/prompt", "Edit additional context"),
    ("/clear", "Clear output window"),
    ("/new-session", "Clear session data"),
    ("/model", "Set AI model"),
    ("/provider", "Select AI provider"),
    ("/help", "Show available commands"),
]

VALID_COMMANDS = [cmd[0] for cmd in COMMANDS_DATA]


def build_commands_list():
    """Build list of commands for autocomplete dropdown."""
    max_cmd_len = max(len(cmd) for cmd, _ in COMMANDS_DATA)
    commands_list = []
    for cmd, desc in COMMANDS_DATA:
        display_text = f"{cmd.ljust(max_cmd_len + 2)}[dim]{desc}[/dim]"
        item = DropdownItem(main=Content.from_markup(display_text))
        commands_list.append(item)
    return commands_list


COMMANDS_LIST = build_commands_list()
