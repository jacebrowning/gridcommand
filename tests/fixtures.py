# pylint: disable=redefined-outer-name

import pytest

from gridcommand.app import build
from gridcommand.config import load
from gridcommand import stores


@pytest.fixture
def app():
    """Fixture to create the Flask application."""
    test_app = build(load('test'))
    test_app.service.game_store = stores.GameFileStore()
    return test_app


@pytest.fixture
def client(app):
    """Fixture to create a test client for the application."""
    return app.test_client()
