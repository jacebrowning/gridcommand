"""Configuration for pytest."""
# pylint: disable=W0613,W0621

import json
from unittest.mock import patch

import pytest

from gridcommand.common import logger
from gridcommand import app
from gridcommand import domain
from gridcommand import services
from gridcommand import stores

ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)

GAME_KEY = 'my_game'
PLAYER_CODE = 'my_code'
PLAYERS_COLORS = ['red', 'blue']


log = logger(__name__)


def load(response):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')
    if text:
        return json.loads(text)


# Flask app fixtures


@pytest.fixture
def client(request):
    """Fixture to create a test client for the application."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.service.game_store = stores.GameMemoryStore()
    test_client = app.test_client()
    return test_client


# Domain model fixtures


@pytest.fixture
def game():
    """Fixture to create an empty game."""
    log.info("creating an empty game...")
    game = app.service.create_game(key=GAME_KEY)
    return game


@pytest.fixture
def game_player(game):
    """Fixture to create a game with one player."""
    log.info("adding a player to a game...")
    with patch.object(domain.Players, 'COLORS', PLAYERS_COLORS):
        game.players.create(PLAYER_CODE)
    return game


@pytest.fixture
def game_players(game):
    """Fixture to create a game with two players."""
    with patch.object(domain.Players, 'COLORS', PLAYERS_COLORS):
        game.players.create(PLAYER_CODE)
        game.players.create(PLAYER_CODE)
    return game


@pytest.fixture
def game_started(game):
    """Fixture to create a started game."""
    game.players.create(PLAYER_CODE)
    game.players.create(PLAYER_CODE)
    game.start()
    return game


@pytest.fixture
def player(game):
    """Fixture to create a player for a game."""
    log.info("adding a player to a game...")
    player = game.players.create(PLAYER_CODE)
    return player


@pytest.fixture
def players(game_players):
    """Fixture to create two players for a game."""
    assert len(game_players.players) == 2
    return game_players.players


@pytest.fixture
def turn(game_player):
    """Fixture to create a turn for a player."""
    log.info("adding a turn to a player...")
    turn = domain.Turn()
    log.debug("appending turn...")
    game_player.players[0].turns.append(turn)
    return turn


@pytest.fixture
def turns(game_player):
    """Fixture to create turns for a player."""
    game_player.players[0].turns.append(domain.Turn())
    game_player.players[0].turns.append(domain.Turn())
    return game_player.players[0].turns


# Service fixtures


@pytest.fixture
def game_service():
    """Fixture to create a game service with memory store."""
    game_store = stores.GameMemoryStore()
    service = services.GameService(game_store=game_store)
    return service
