"""Shared pytest fixtures."""
import pytest

from src.app import create_app
from src.notifications.notification_service import NotificationService


@pytest.fixture
def app():
    """Create app in test mode."""
    application = create_app({"TESTING": True})
    yield application


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_service():
    """Reset in-memory stores before every test."""
    NotificationService.reset()
    yield
    NotificationService.reset()
