"""Custom exceptions for Cyclon application."""


class CyclonError(Exception):
    """Base exception for all Cyclon errors."""

    pass


class ConfigError(CyclonError):
    """Exception raised for configuration-related errors."""

    pass


class FileError(CyclonError):
    """Exception raised for file operation errors."""

    pass


class ProcessError(CyclonError):
    """Exception raised for process-related errors."""

    pass


class ValidationError(CyclonError):
    """Exception raised for validation errors."""

    pass
