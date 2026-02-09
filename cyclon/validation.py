"""Validation utilities for Cyclon application."""

from typing import TypeVar, Type, Optional, List, Any

T = TypeVar('T')


def validate_string(
    value: Any, 
    name: str, 
    allow_empty: bool = False
) -> str:
    """Validate that value is a string.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        allow_empty: Whether empty strings are allowed
        
    Returns:
        str: The validated string value
        
    Raises:
        ValueError: If value is None, not a string, or empty (when not allowed)
        
    Example:
        >>> validate_string("hello", "username")
        'hello'
        >>> validate_string("", "username")
        ValueError: username must be a non-empty string
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def validate_optional_string(
    value: Any, 
    name: str
) -> Optional[str]:
    """Validate that value is a string or None.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        
    Returns:
        Optional[str]: The validated string value or None
        
    Raises:
        ValueError: If value is not a string and not None
        
    Example:
        >>> validate_optional_string("hello", "provider")
        'hello'
        >>> validate_optional_string(None, "provider")
        None
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string or None")
    return value


def validate_list(
    value: Any,
    name: str,
    item_type: Optional[Type[T]] = None,
    min_length: Optional[int] = None
) -> List[T]:
    """Validate that value is a list.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        item_type: Expected type of list items (optional)
        min_length: Minimum required length (optional)
        
    Returns:
        List[T]: The validated list
        
    Raises:
        ValueError: If value is not a valid list
        
    Example:
        >>> validate_list(["a", "b"], "items", item_type=str, min_length=1)
        ['a', 'b']
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    if min_length is not None and len(value) < min_length:
        raise ValueError(f"{name} must have at least {min_length} items")
    if item_type is not None:
        if not all(isinstance(item, item_type) for item in value):
            type_name = item_type.__name__
            raise ValueError(f"All items in {name} must be {type_name}")
    return value


def validate_positive_int(value: Any, name: str) -> int:
    """Validate that value is a positive integer.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        
    Returns:
        int: The validated integer value
        
    Raises:
        ValueError: If value is not a positive integer
        
    Example:
        >>> validate_positive_int(10, "timeout")
        10
        >>> validate_positive_int(0, "timeout")
        ValueError: timeout must be a positive integer
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def validate_not_none(value: Any, name: str) -> Any:
    """Validate that value is not None.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        
    Returns:
        Any: The validated value
        
    Raises:
        ValueError: If value is None
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    return value
