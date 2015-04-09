"""Unit tests for the `api.game` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from unittest.mock import patch, Mock

from ..conftest import load

from . import GAMES


class TestGames:

    def test_get_games_list_hidden(self, client):
        response = client.get('/api/games/')
        assert 403 == response.status_code
        assert {'message':
                "Games list is hidden."} == load(response)

    @patch('gridcommand.models.game.Game._generate_key', Mock(return_value='x'))
    def test_post_new_game(self, client):
        response = client.post('/api/games/')
        assert 201 == response.status_code
        assert {'key': "x",
                'players': GAMES + "x/players/",
                'start': GAMES + "x/start",
                'phase': 0} == load(response)


class TestGame:

    def test_get_existing_game(self, client, game):
        response = client.get('/api/games/my_game')
        assert 200 == response.status_code
        assert {'key': "my_game",
                'players': GAMES + "my_game/players/",
                'start': GAMES + "my_game/start",
                'phase': 0} == load(response)

    def test_get_missing_game(self, client):
        response = client.get('/api/games/my_game')
        assert 404 == response.status_code
        assert {'message':
                "The game 'my_game' does not exist."} == load(response)


class TestGameStart:

    def test_get_not_started(self, client, game):
        response = client.get('/api/games/my_game/start')
        assert 200 == response.status_code
        assert {'started': False} == load(response)

    def test_get_started(self, client, game_started):
        response = client.get('/api/games/my_game/start')
        assert 200 == response.status_code
        assert {'started': True} == load(response)

    def test_post_start_game(self, client, game_players):
        response = client.post('/api/games/my_game/start')
        assert 200 == response.status_code
        assert {'started': True} == load(response)

    def test_post_start_game_requires_players(self, client, game_player):
        response = client.post('/api/games/my_game/start')
        assert 403 == response.status_code
        assert {'message':
                "At least 2 players are required."} == load(response)