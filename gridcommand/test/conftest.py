"""Configuration for pytest."""
# pylint: disable=W0613

import os
import json
import pytest

import yorm

from gridcommand import app
from gridcommand import data

ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)


def pytest_runtest_setup(item):
    """pytest setup."""
    if 'integration' in item.keywords:
        if not os.getenv(ENV):
            pytest.skip(REASON)
        else:
            yorm.settings.fake = False
    else:
        yorm.settings.fake = True


@pytest.fixture
def client(request):
    """Fixture to create a test client for the application."""
    test_client = app.test_client()
    data.games.clear()
    return test_client


def load(response):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')
    return json.loads(text)
