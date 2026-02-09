"""Unit tests for constants module."""

import pytest
from textual_autocomplete._autocomplete import DropdownItem

from cyclon.constants import (
    CONFIG_FILENAME,
    PLAN_FILENAME,
    PROMPT_FILENAME,
    LOCK_FILENAME,
    CONTEXT_FILENAME,
    PLAN_GENERATION_TIMEOUT,
    EXECUTION_TIMEOUT,
    EXCEPTION_RETRY_DELAY,
    PROCESS_TERMINATION_DELAY,
    LOG_MAX_LINES,
    COMMANDS_DATA,
    VALID_COMMANDS,
    build_commands_list,
    COMMANDS_LIST,
)


class TestFilenameConstants:
    """Tests for filename constants."""

    def test_config_filename(self):
        """CONFIG_FILENAME should be 'config.json'."""
        assert CONFIG_FILENAME == "config.json"

    def test_plan_filename(self):
        """PLAN_FILENAME should be 'plan.md'."""
        assert PLAN_FILENAME == "plan.md"

    def test_prompt_filename(self):
        """PROMPT_FILENAME should be 'prompt.md'."""
        assert PROMPT_FILENAME == "prompt.md"

    def test_lock_filename(self):
        """LOCK_FILENAME should be 'process.lock'."""
        assert LOCK_FILENAME == "process.lock"

    def test_context_filename(self):
        """CONTEXT_FILENAME should be 'context.md'."""
        assert CONTEXT_FILENAME == "context.md"


class TestTimeoutConstants:
    """Tests for timeout and delay constants."""

    def test_plan_generation_timeout(self):
        """PLAN_GENERATION_TIMEOUT should be 600."""
        assert PLAN_GENERATION_TIMEOUT == 600
        assert isinstance(PLAN_GENERATION_TIMEOUT, int)

    def test_execution_timeout(self):
        """EXECUTION_TIMEOUT should be 3600."""
        assert EXECUTION_TIMEOUT == 3600
        assert isinstance(EXECUTION_TIMEOUT, int)

    def test_exception_retry_delay(self):
        """EXCEPTION_RETRY_DELAY should be 10."""
        assert EXCEPTION_RETRY_DELAY == 10
        assert isinstance(EXCEPTION_RETRY_DELAY, int)

    def test_process_termination_delay(self):
        """PROCESS_TERMINATION_DELAY should be 0.1."""
        assert PROCESS_TERMINATION_DELAY == 0.1
        assert isinstance(PROCESS_TERMINATION_DELAY, float)


class TestUIConstants:
    """Tests for UI constants."""

    def test_log_max_lines(self):
        """LOG_MAX_LINES should be 10000."""
        assert LOG_MAX_LINES == 10000
        assert isinstance(LOG_MAX_LINES, int)


class TestCommandsConstants:
    """Tests for commands-related constants."""

    def test_commands_data_type(self):
        """COMMANDS_DATA should be a list of tuples."""
        assert isinstance(COMMANDS_DATA, list)
        assert all(isinstance(cmd, tuple) for cmd in COMMANDS_DATA)
        assert all(len(cmd) == 2 for cmd in COMMANDS_DATA)

    def test_commands_data_content(self):
        """COMMANDS_DATA should contain all expected commands."""
        command_names = [cmd[0] for cmd in COMMANDS_DATA]
        expected_commands = [
            "/plan",
            "/run",
            "/stop",
            "/prompt",
            "/clear",
            "/new-session",
            "/model",
            "/provider",
            "/help",
        ]
        for cmd in expected_commands:
            assert cmd in command_names, f"Missing command: {cmd}"

    def test_commands_data_descriptions(self):
        """COMMANDS_DATA should have descriptions for all commands."""
        for cmd, desc in COMMANDS_DATA:
            assert isinstance(cmd, str)
            assert isinstance(desc, str)
            assert cmd.startswith("/")
            assert len(desc) > 0

    def test_valid_commands_type(self):
        """VALID_COMMANDS should be a list of strings."""
        assert isinstance(VALID_COMMANDS, list)
        assert all(isinstance(cmd, str) for cmd in VALID_COMMANDS)

    def test_valid_commands_content(self):
        """VALID_COMMANDS should contain only command names."""
        assert "/plan" in VALID_COMMANDS
        assert "/run" in VALID_COMMANDS
        assert "/stop" in VALID_COMMANDS
        assert "/help" in VALID_COMMANDS

    def test_valid_commands_derived_from_commands_data(self):
        """VALID_COMMANDS should be derived from COMMANDS_DATA."""
        expected = [cmd[0] for cmd in COMMANDS_DATA]
        assert VALID_COMMANDS == expected

    def test_commands_data_and_valid_commands_same_length(self):
        """COMMANDS_DATA and VALID_COMMANDS should have same length."""
        assert len(COMMANDS_DATA) == len(VALID_COMMANDS)


class TestBuildCommandsList:
    """Tests for build_commands_list function."""

    def test_returns_list(self):
        """Should return a list."""
        result = build_commands_list()
        assert isinstance(result, list)

    def test_returns_dropdown_items(self):
        """Should return list of DropdownItem objects."""
        result = build_commands_list()
        assert all(isinstance(item, DropdownItem) for item in result)

    def test_returns_correct_number_of_items(self):
        """Should return same number of items as COMMANDS_DATA."""
        result = build_commands_list()
        assert len(result) == len(COMMANDS_DATA)

    def test_items_have_main_attribute(self):
        """Each DropdownItem should have main attribute."""
        result = build_commands_list()
        for item in result:
            assert hasattr(item, 'main')
            assert item.main is not None


class TestCommandsList:
    """Tests for COMMANDS_LIST constant."""

    def test_is_precomputed(self):
        """COMMANDS_LIST should be precomputed (not None)."""
        assert COMMANDS_LIST is not None

    def test_is_list(self):
        """COMMANDS_LIST should be a list."""
        assert isinstance(COMMANDS_LIST, list)

    def test_contains_dropdown_items(self):
        """COMMANDS_LIST should contain DropdownItem objects."""
        assert all(isinstance(item, DropdownItem) for item in COMMANDS_LIST)

    def test_matches_build_commands_list(self):
        """COMMANDS_LIST should match build_commands_list() result."""
        built = build_commands_list()
        assert len(COMMANDS_LIST) == len(built)
        # Compare string representations since DropdownItem doesn't have __eq__
        for i, (cached, fresh) in enumerate(zip(COMMANDS_LIST, built)):
            assert str(cached.main) == str(fresh.main)


class TestConstantsAreImmutable:
    """Tests ensuring constants are treated as immutable."""

    def test_modifying_commands_data_does_not_affect_valid_commands(self):
        """Modifying copy of COMMANDS_DATA should not affect VALID_COMMANDS."""
        original_valid = VALID_COMMANDS.copy()
        commands_copy = COMMANDS_DATA.copy()
        if commands_copy:
            commands_copy.pop()
        # VALID_COMMANDS should be unchanged
        assert VALID_COMMANDS == original_valid

    def test_creating_new_list_from_commands_data(self):
        """Should be able to create new list from COMMANDS_DATA."""
        new_list = list(COMMANDS_DATA)
        assert new_list == COMMANDS_DATA
        assert new_list is not COMMANDS_DATA
