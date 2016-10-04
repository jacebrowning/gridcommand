"""Integration tests configuration file."""
# pylint: disable=unused-argument,wildcard-import,unused-wildcard-import

import json
import logging

import pytest

from gridcommand.common import logger
from gridcommand import app

from gridcommand.tests.conftest import pytest_configure  # pylint: disable=unused-import


log = logger(__name__)


def load(response):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')
    if text:
        data = json.loads(text)
    else:
        data = None
    logging.debug("response: %r", data)
    return data


@pytest.fixture
def client(request):
    """Fixture to create a test client for the application."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    test_client = app.test_client()
    return test_client
