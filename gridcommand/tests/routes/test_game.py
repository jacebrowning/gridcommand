"""Unit tests for the `views.game` module."""
# pylint: disable=no-self-use
# pylint: disable=unused-argument,expression-not-assigned,misplaced-comparison-constant

from unittest.mock import patch, Mock

from expecter import expect

from ..conftest import load

from . import GAMES, EXTERNAL


class TestGames:

    def test_get_games_list_hidden(self, client):
        response = client.get(GAMES)
        expect(response.status_code) == 200
        expect(load(response)) == []

    @patch('gridcommand.domain.game.Game._generate_key', Mock(return_value='x'))
    @patch('gridcommand.domain.game.Game._get_timestamp', Mock(return_value=99))
    def test_post_new_game(self, client):
        response = client.post(GAMES)
        assert 201 == response.status_code
        assert {
            'uri': EXTERNAL + GAMES + "x",
            'timestamp': 99,
            'players': EXTERNAL + GAMES + "x/players/",
            'turn': 0,
            'start': EXTERNAL + GAMES + "x/start",
        } == load(response)


class TestGame:

    def test_get_existing_game(self, client, game):
        response = client.get(GAMES + "my_game")
        assert 200 == response.status_code
        assert {
            'uri': EXTERNAL + GAMES + "my_game",
            'timestamp': 99,
            'players': EXTERNAL + GAMES + "my_game/players/",
            'turn': 0,
            'start': EXTERNAL + GAMES + "my_game/start",
        } == load(response)

    def test_get_missing_game(self, client):
        response = client.get(GAMES + "my_game")
        assert 404 == response.status_code
        assert {
            'message': "The game 'my_game' does not exist.",
        } == load(response)


class TestGameStart:

    START = GAMES + "my_game/start"

    def test_get_not_started(self, client, game):
        response = client.get(self.START)
        assert 200 == response.status_code
        assert {'started': False} == load(response)

    def test_get_started(self, client, game_started):
        response = client.get(self.START)
        assert 200 == response.status_code
        assert {'started': True} == load(response)

    def test_post_start_game(self, client, game_players):
        response = client.post(self.START)
        assert 200 == response.status_code
        assert {'started': True} == load(response)

    def test_post_start_game_already_started(self, client, game_started):
        response = client.post(self.START)
        assert 403 == response.status_code
        assert {
            'message': "The game has already started.",
        } == load(response)

    def test_post_start_game_requires_players(self, client, game_player):
        response = client.post(self.START)
        assert 403 == response.status_code
        assert {
            'message': "At least 2 players are required.",
        } == load(response)


class TestGameBoard:

    BOARD = GAMES + "my_game/board"

    def test_get_not_started(self, client, game):
        response = client.get(self.BOARD)
        assert 404 == response.status_code
        assert {'message': "The game has not started."} == load(response)

    def test_get_started(self, client, game_started):
        response = client.get(self.BOARD)
        assert 200 == response.status_code
        assert {} == load(response)
