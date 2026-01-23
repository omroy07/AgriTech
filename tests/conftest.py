import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config.update({
        'TESTING': True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the application's CLI commands."""
    return app.test_cli_runner()
