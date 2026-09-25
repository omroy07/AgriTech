"""
Tests for startup configuration validation, specifically validating that
missing GEMINI_API_KEY causes the application to fail fast with a clear error.
"""

import pytest
from flask import Flask
from backend.config import validate_required_config


class TestGeminiConfigValidation:
    def test_missing_gemini_api_key_raises_value_error(self):
        app = Flask(__name__)
        app.config['TESTING'] = False
        app.config['GEMINI_API_KEY'] = None

        with pytest.raises(ValueError, match="CRITICAL STARTUP ERROR: GEMINI_API_KEY is missing or empty"):
            validate_required_config(app)

    def test_empty_string_gemini_api_key_raises_value_error(self):
        app = Flask(__name__)
        app.config['TESTING'] = False
        app.config['GEMINI_API_KEY'] = "   "

        with pytest.raises(ValueError, match="CRITICAL STARTUP ERROR: GEMINI_API_KEY is missing or empty"):
            validate_required_config(app)

    def test_valid_gemini_api_key_passes_validation(self):
        app = Flask(__name__)
        app.config['TESTING'] = False
        app.config['GEMINI_API_KEY'] = "valid-gemini-api-key-12345"

        # Should not raise any exception
        validate_required_config(app)

    def test_testing_mode_bypasses_strict_validation(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['GEMINI_API_KEY'] = None

        # When TESTING=True, it allows test harness execution without requiring a live production API key
        validate_required_config(app)
