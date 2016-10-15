# pylint: disable=redefined-outer-name

import logging
from unittest.mock import patch

import pytest

from gridcommand.app import build
from gridcommand.config import load
from gridcommand import domain
from gridcommand import services
from gridcommand import stores


GAME_KEY = 'my_game'
PLAYER_CODE = 'my_code'
PLAYERS_COLORS = ['red', 'blue']

log = logging.getLogger(__name__)


# Flask app fixtures


@pytest.fixture
def app():
    """Fixture to create the Flask application."""
    test_app = build(load('test'))
    test_app.service.game_store = stores.GameMemoryStore()
    return test_app


@pytest.fixture
def client(app):
    """Fixture to create a test client for the application."""
    return app.test_client()


# Domain model fixtures


@pytest.fixture
def game(app):
    """Fixture to create an empty game."""
    log.info("creating an empty game...")
    game = app.service.create_game(key=GAME_KEY, timestamp=99)
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
def game_started(game_players):
    """Fixture to create a started game."""
    game_players.start()
    return game_players


@pytest.fixture
def game_turns(game_started):
    """Fixture to create a game with multiple turns."""
    game_started.advance()
    return game_started


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
def turn(game_started):
    """Fixture to create a turn for a player."""
    assert game_started.turn == 1
    turn = game_started.players[0].turn
    assert not turn.done
    return turn


@pytest.fixture
def turn_completed(turn):
    """Fixture to create a completed turn for a player."""
    turn.finish()
    assert turn.done
    return turn


# Service fixtures


@pytest.fixture
def game_service():
    """Fixture to create a game service with memory store."""
    game_store = stores.GameMemoryStore()
    service = services.GameService(game_store=game_store)
    return service
