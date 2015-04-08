"""Configuration for pytest."""
# pylint: disable=W0613,W0621

import os
import json
import pytest

import yorm

from gridcommand import app
from gridcommand import models
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
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    test_client = app.test_client()
    data.games.clear()
    return test_client


@pytest.fixture
def game():
    """Fixture to create an empty game."""
    game = models.Game('my_game')
    data.games[game.key] = game
    return game


@pytest.fixture
def game_player(game):
    """Fixture to create a game with one player."""
    game.players.create('my_code')
    yorm.update(game)  # TODO: remove when unnecessary
    return game


@pytest.fixture
def game_players(game):
    """Fixture to create a game with two players."""
    game.players.create('my_code')
    game.players.create('my_code')
    yorm.update(game)  # TODO: remove when unnecessary
    return game


@pytest.fixture
def game_started(game):
    """Fixture to create a started game."""
    game.players.create('my_code')
    game.players.create('my_code')
    game.start()
    yorm.update(game)  # TODO: remove when unnecessary
    return game


@pytest.fixture
def player(game):
    """Fixture to create a player for a game."""
    player = game.players.create('my_code')
    yorm.update(game)  # TODO: remove when unnecessary
    assert 'red' == player.color
    return player


@pytest.fixture
def phase(game):
    """Fixture to create a phase for a player."""
    player = game.players.create('my_code')
    phase = models.Phase()
    player.phases.append(phase)
    yorm.update(game)  # TODO: remove when unnecessary
    return phase


def load(response):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')
    return json.loads(text)
