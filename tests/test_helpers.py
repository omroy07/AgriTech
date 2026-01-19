import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import sanitize_input, validate_input


class TestSanitizeInput:
    """Test suite for the sanitize_input helper function."""

    def test_sanitize_removes_html_tags(self):
        """Test that HTML tags are removed from input."""
        result = sanitize_input("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_sanitize_escapes_special_characters(self):
        """Test that special characters are escaped."""
        result = sanitize_input("Hello & World")
        assert "&amp;" in result

    def test_sanitize_limits_length(self):
        """Test that input is limited to 1000 characters."""
        long_input = "a" * 1500
        result = sanitize_input(long_input)
        assert len(result) <= 1000

    def test_sanitize_handles_none(self):
        """Test that None input returns empty string."""
        result = sanitize_input(None)
        assert result == ""

    def test_sanitize_handles_non_string(self):
        """Test that non-string input returns empty string."""
        result = sanitize_input(123)
        assert result == ""

    def test_sanitize_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        result = sanitize_input("  hello world  ")
        assert result == "hello world"


class TestValidateInput:
    """Test suite for the validate_input helper function."""

    def test_validate_returns_false_for_none(self):
        """Test that None data returns False."""
        is_valid, message = validate_input(None)
        assert is_valid is False
        assert "No data provided" in message

    def test_validate_returns_false_for_empty_dict(self):
        """Test that empty dict returns False."""
        is_valid, message = validate_input({})
        assert is_valid is False

    def test_validate_returns_true_for_valid_data(self):
        """Test that valid dict returns True."""
        is_valid, message = validate_input({"key": "value"})
        assert is_valid is True
        assert "Valid" in message
