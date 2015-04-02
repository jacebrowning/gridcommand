"""Configuration for pytest."""
# pylint: disable=W0613

import os
import json
import pytest

import yorm

from gridcommand import views

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
    test_client = views.app.test_client()
    views.games.clear()
    return test_client


def load(response):
    text = response.data.decode('utf-8')
    return json.loads(text)
