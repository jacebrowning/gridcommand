"""Configuration for pytest."""
# pylint: disable=W0613,W0621

import os
import json
from unittest.mock import patch

import pytest
import yorm

from gridcommand import app
from gridcommand import models
from gridcommand import data

ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)

GAME_KEY = 'my_game'
PLAYER_CODE = 'my_code'
PLAYERS_COLORS = ['red', 'blue']


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
    game = models.Game(GAME_KEY)
    data.games[game.key] = game
    return game


@pytest.fixture
def game_player(game):
    """Fixture to create a game with one player."""
    with patch.object(models.Players, 'COLORS', PLAYERS_COLORS):
        game.players.create(PLAYER_CODE)
    yorm.update(game)  # TODO: remove when unnecessary
    return game


@pytest.fixture
def game_players(game):
    """Fixture to create a game with two players."""
    with patch.object(models.Players, 'COLORS', PLAYERS_COLORS):
        game.players.create(PLAYER_CODE)
        game.players.create(PLAYER_CODE)
    yorm.update(game)  # TODO: remove when unnecessary
    return game


@pytest.fixture
def game_started(game):
    """Fixture to create a started game."""
    game.players.create(PLAYER_CODE)
    game.players.create(PLAYER_CODE)
    game.start()
    yorm.update(game)  # TODO: remove when unnecessary
    return game


@pytest.fixture
def player(game):
    """Fixture to create a player for a game."""
    player = game.players.create(PLAYER_CODE)
    yorm.update(game)  # TODO: remove when unnecessary
    return player


@pytest.fixture
def players(game_players):
    """Fixture to create two players for a game."""
    return game_players.players


@pytest.fixture
def phases(player):
    """Fixture to create empty phases for a player."""
    return player.phases


@pytest.fixture
def phase(game):
    """Fixture to create a phase for a player."""
    player = game.players.create(PLAYER_CODE)
    phase = models.Phase()
    player.phases.append(phase)
    yorm.update(game)  # TODO: remove when unnecessary
    return phase


def load(response):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')
    return json.loads(text)
