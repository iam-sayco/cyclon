"""Unit tests for exceptions module."""

import pytest

from cyclon.exceptions import (
    ConfigError,
    CyclonError,
    FileError,
    ProcessError,
    ValidationError,
)


class TestCyclonError:
    """Tests for CyclonError base exception."""

    def test_can_initialize_with_message(self):
        """Should initialize with a message."""
        exc = CyclonError("Test error message")
        assert str(exc) == "Test error message"

    def test_is_instance_of_exception(self):
        """Should be instance of Python Exception."""
        exc = CyclonError("Test")
        assert isinstance(exc, Exception)

    def test_can_be_caught_as_exception(self):
        """Should be catchable as Exception."""
        try:
            raise CyclonError("Test")
        except Exception as e:
            assert isinstance(e, CyclonError)
            assert str(e) == "Test"

    def test_preserves_error_message(self):
        """Should preserve error message."""
        message = "Something went wrong"
        exc = CyclonError(message)
        assert exc.args[0] == message

    def test_empty_message(self):
        """Should work with empty message."""
        exc = CyclonError("")
        assert str(exc) == ""


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_can_initialize_with_message(self):
        """Should initialize with a message."""
        exc = ConfigError("Config file not found")
        assert str(exc) == "Config file not found"

    def test_is_instance_of_cyclon_error(self):
        """Should be instance of CyclonError (hierarchy)."""
        exc = ConfigError("Test")
        assert isinstance(exc, CyclonError)

    def test_is_instance_of_exception(self):
        """Should be instance of Exception."""
        exc = ConfigError("Test")
        assert isinstance(exc, Exception)

    def test_can_be_caught_as_cyclon_error(self):
        """Should be catchable as CyclonError."""
        try:
            raise ConfigError("Test")
        except CyclonError as e:
            assert isinstance(e, ConfigError)

    def test_preserves_error_message(self):
        """Should preserve error message."""
        message = "Invalid JSON in config"
        exc = ConfigError(message)
        assert str(exc) == message


class TestFileError:
    """Tests for FileError exception."""

    def test_can_initialize_with_message(self):
        """Should initialize with a message."""
        exc = FileError("File not found")
        assert str(exc) == "File not found"

    def test_is_instance_of_cyclon_error(self):
        """Should be instance of CyclonError (hierarchy)."""
        exc = FileError("Test")
        assert isinstance(exc, CyclonError)

    def test_is_instance_of_exception(self):
        """Should be instance of Exception."""
        exc = FileError("Test")
        assert isinstance(exc, Exception)

    def test_can_be_caught_as_cyclon_error(self):
        """Should be catchable as CyclonError."""
        try:
            raise FileError("Test")
        except CyclonError as e:
            assert isinstance(e, FileError)

    def test_preserves_error_message(self):
        """Should preserve error message."""
        message = "Error reading file"
        exc = FileError(message)
        assert str(exc) == message


class TestProcessError:
    """Tests for ProcessError exception."""

    def test_can_initialize_with_message(self):
        """Should initialize with a message."""
        exc = ProcessError("Process failed")
        assert str(exc) == "Process failed"

    def test_is_instance_of_cyclon_error(self):
        """Should be instance of CyclonError (hierarchy)."""
        exc = ProcessError("Test")
        assert isinstance(exc, CyclonError)

    def test_is_instance_of_exception(self):
        """Should be instance of Exception."""
        exc = ProcessError("Test")
        assert isinstance(exc, Exception)

    def test_can_be_caught_as_cyclon_error(self):
        """Should be catchable as CyclonError."""
        try:
            raise ProcessError("Test")
        except CyclonError as e:
            assert isinstance(e, ProcessError)

    def test_preserves_error_message(self):
        """Should preserve error message."""
        message = "Error writing to process"
        exc = ProcessError(message)
        assert str(exc) == message


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_can_initialize_with_message(self):
        """Should initialize with a message."""
        exc = ValidationError("Invalid input")
        assert str(exc) == "Invalid input"

    def test_is_instance_of_cyclon_error(self):
        """Should be instance of CyclonError (hierarchy)."""
        exc = ValidationError("Test")
        assert isinstance(exc, CyclonError)

    def test_is_instance_of_exception(self):
        """Should be instance of Exception."""
        exc = ValidationError("Test")
        assert isinstance(exc, Exception)

    def test_can_be_caught_as_cyclon_error(self):
        """Should be catchable as CyclonError."""
        try:
            raise ValidationError("Test")
        except CyclonError as e:
            assert isinstance(e, ValidationError)

    def test_preserves_error_message(self):
        """Should preserve error message."""
        message = "Field cannot be None"
        exc = ValidationError(message)
        assert str(exc) == message


class TestExceptionHierarchy:
    """Tests for exception hierarchy behavior."""

    def test_all_exceptions_catchable_as_cyclon_error(self):
        """All custom exceptions should be catchable as CyclonError."""
        exceptions = [ConfigError, FileError, ProcessError, ValidationError]

        for exc_class in exceptions:
            try:
                raise exc_class("Test message")
            except CyclonError as e:
                assert isinstance(e, exc_class)
                assert str(e) == "Test message"

    def test_all_exceptions_catchable_as_exception(self):
        """All custom exceptions should be catchable as Exception."""
        exceptions = [CyclonError, ConfigError, FileError, ProcessError, ValidationError]

        for exc_class in exceptions:
            try:
                raise exc_class("Test message")
            except Exception as e:
                assert isinstance(e, exc_class)

    def test_specific_exception_not_caught_by_other(self):
        """Specific exceptions should not be caught by other specific handlers."""
        try:
            raise ConfigError("Config error")
        except FileError:
            pytest.fail("ConfigError should not be caught by FileError")
        except ConfigError:
            pass  # Expected

    def test_catch_order_matters(self):
        """Exception catch order should matter (most specific first)."""
        caught = None
        try:
            raise ConfigError("Test")
        except ConfigError:
            caught = "ConfigError"
        except CyclonError:
            caught = "CyclonError"

        assert caught == "ConfigError"
