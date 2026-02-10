"""Unit tests for validation module."""

import pytest

from cyclon.validation import (
    validate_list,
    validate_not_none,
    validate_optional_string,
    validate_positive_int,
    validate_string,
)


class TestValidateString:
    """Tests for validate_string function."""

    def test_valid_non_empty_string(self):
        """Should return value for valid non-empty string."""
        result = validate_string("hello", "username")
        assert result == "hello"

    def test_empty_string_with_allow_empty_true(self):
        """Should return value for empty string when allow_empty=True."""
        result = validate_string("", "field", allow_empty=True)
        assert result == ""

    def test_empty_string_with_allow_empty_false(self):
        """Should raise ValueError for empty string when allow_empty=False."""
        with pytest.raises(ValueError, match="field must be a non-empty string"):
            validate_string("", "field")

    def test_none_value(self):
        """Should raise ValueError for None."""
        with pytest.raises(ValueError, match="field cannot be None"):
            validate_string(None, "field")

    def test_integer_value(self):
        """Should raise ValueError for integer."""
        with pytest.raises(ValueError, match="field must be a string"):
            validate_string(123, "field")

    def test_list_value(self):
        """Should raise ValueError for list."""
        with pytest.raises(ValueError, match="field must be a string"):
            validate_string(["a", "b"], "field")

    def test_dict_value(self):
        """Should raise ValueError for dict."""
        with pytest.raises(ValueError, match="field must be a string"):
            validate_string({"key": "value"}, "field")


class TestValidateOptionalString:
    """Tests for validate_optional_string function."""

    def test_valid_non_empty_string(self):
        """Should return value for valid non-empty string."""
        result = validate_optional_string("hello", "provider")
        assert result == "hello"

    def test_none_value(self):
        """Should return None for None input."""
        result = validate_optional_string(None, "provider")
        assert result is None

    def test_empty_string(self):
        """Should return empty string for empty input."""
        result = validate_optional_string("", "provider")
        assert result == ""

    def test_integer_value(self):
        """Should raise ValueError for integer."""
        with pytest.raises(ValueError, match="provider must be a string or None"):
            validate_optional_string(123, "provider")

    def test_list_value(self):
        """Should raise ValueError for list."""
        with pytest.raises(ValueError, match="provider must be a string or None"):
            validate_optional_string(["a", "b"], "provider")


class TestValidateList:
    """Tests for validate_list function."""

    def test_valid_string_list(self):
        """Should return list for valid string list."""
        result = validate_list(["a", "b", "c"], "items")
        assert result == ["a", "b", "c"]

    def test_valid_int_list_with_item_type(self):
        """Should return list for valid int list with item_type."""
        result = validate_list([1, 2, 3], "items", item_type=int)
        assert result == [1, 2, 3]

    def test_empty_list_with_min_length_zero(self):
        """Should return empty list when min_length=0."""
        result = validate_list([], "items", min_length=0)
        assert result == []

    def test_none_value(self):
        """Should raise ValueError for None."""
        with pytest.raises(ValueError, match="items cannot be None"):
            validate_list(None, "items")

    def test_string_instead_of_list(self):
        """Should raise ValueError for string instead of list."""
        with pytest.raises(ValueError, match="items must be a list"):
            validate_list("not a list", "items")

    def test_list_shorter_than_min_length(self):
        """Should raise ValueError for list shorter than min_length."""
        with pytest.raises(ValueError, match="items must have at least 3 items"):
            validate_list(["a", "b"], "items", min_length=3)

    def test_list_with_wrong_item_type(self):
        """Should raise ValueError for list with wrong item type."""
        with pytest.raises(ValueError, match="All items in items must be str"):
            validate_list([1, 2, 3], "items", item_type=str)

    def test_list_with_mixed_types(self):
        """Should raise ValueError for list with mixed types."""
        with pytest.raises(ValueError, match="All items in items must be int"):
            validate_list([1, "two", 3], "items", item_type=int)


class TestValidatePositiveInt:
    """Tests for validate_positive_int function."""

    def test_one(self):
        """Should return 1 for input 1."""
        result = validate_positive_int(1, "timeout")
        assert result == 1

    def test_hundred(self):
        """Should return 100 for input 100."""
        result = validate_positive_int(100, "timeout")
        assert result == 100

    def test_zero(self):
        """Should raise ValueError for 0."""
        with pytest.raises(ValueError, match="timeout must be a positive integer"):
            validate_positive_int(0, "timeout")

    def test_negative(self):
        """Should raise ValueError for negative number."""
        with pytest.raises(ValueError, match="timeout must be a positive integer"):
            validate_positive_int(-1, "timeout")

    def test_none_value(self):
        """Should raise ValueError for None."""
        with pytest.raises(ValueError, match="timeout cannot be None"):
            validate_positive_int(None, "timeout")

    def test_string_number(self):
        """Should raise ValueError for string number."""
        with pytest.raises(ValueError, match="timeout must be an integer"):
            validate_positive_int("10", "timeout")

    def test_boolean_true(self):
        """Should raise ValueError for boolean True (isinstance(True, int))."""
        with pytest.raises(ValueError, match="timeout must be an integer"):
            validate_positive_int(True, "timeout")

    def test_boolean_false(self):
        """Should raise ValueError for boolean False."""
        with pytest.raises(ValueError, match="timeout must be an integer"):
            validate_positive_int(False, "timeout")

    def test_float(self):
        """Should raise ValueError for float."""
        with pytest.raises(ValueError, match="timeout must be an integer"):
            validate_positive_int(10.5, "timeout")


class TestValidateNotNone:
    """Tests for validate_not_none function."""

    def test_string(self):
        """Should return string for string input."""
        result = validate_not_none("hello", "field")
        assert result == "hello"

    def test_empty_string(self):
        """Should return empty string for empty string input."""
        result = validate_not_none("", "field")
        assert result == ""

    def test_zero(self):
        """Should return 0 for 0 input."""
        result = validate_not_none(0, "field")
        assert result == 0

    def test_false(self):
        """Should return False for False input."""
        result = validate_not_none(False, "field")
        assert result is False

    def test_none_value(self):
        """Should raise ValueError for None."""
        with pytest.raises(ValueError, match="field cannot be None"):
            validate_not_none(None, "field")

    def test_empty_list(self):
        """Should return empty list for empty list input."""
        result = validate_not_none([], "field")
        assert result == []
