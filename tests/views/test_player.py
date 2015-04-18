"""Unit tests for the `api.player` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES


class TestPlayers:

    def test_get_players(self, client, game_players):
        response = client.get('/api/games/my_game/players/')
        assert 200 == response.status_code
        assert [GAMES + "my_game/players/red",
                GAMES + "my_game/players/blue"] == load(response)

    def test_post_player(self, client, game):
        response = client.post('/api/games/my_game/players/',
                               data={'code': "1234"})
        assert 201 == response.status_code
        assert {'color': "red",
                'code': '1234',
                'turns': GAMES + "my_game/players/red-1234/turns/",
                'turn': 0} == load(response)

    def test_post_player_with_invalid_code(self, client, game):
        response = client.post('/api/games/my_game/players/')
        assert 400 == response.status_code
        assert {'message':
                "Player 'code' must be specified."} == load(response)

    def test_post_player_after_game_start(self, client, game_started):
        response = client.post('/api/games/my_game/players/',
                               data={'code': "1234"})
        assert 403 == response.status_code
        assert {'message':
                "Game has already started."} == load(response)


class TestPlayer:

    def test_get_existing_player(self, client, player):
        response = client.get('/api/games/my_game/players/red')
        assert 200 == response.status_code
        assert {'color': "red",
                'turn': 0} == load(response)

    def test_get_missing_player(self, client, game):
        response = client.get('/api/games/my_game/players/red')
        assert 404 == response.status_code
        assert {'message':
                "The player 'red' does not exist."} == load(response)


class TestPlayerAuth:

    def test_get_existing_player(self, client, player):
        response = client.get('/api/games/my_game/players/red-my_code')
        assert 200 == response.status_code
        assert {'color': "red",
                'code': 'my_code',
                'turns': GAMES + "my_game/players/red-my_code/turns/",
                'turn': 0} == load(response)

    def test_get_existing_player_with_bad_auth(self, client, player):
        response = client.get('/api/games/my_game/players/red-invalid')
        assert 401 == response.status_code
        assert {'message': "The code 'invalid' is invalid."}

    def test_delete_player(self, client, player):
        response = client.delete('/api/games/my_game/players/red-my_code')
        assert 204 == response.status_code
        assert None is load(response)

    def test_delete_player_after_game_start(self, client, game_started):
        response = client.delete('/api/games/my_game/players/red-my_code')
        assert 403 == response.status_code
        assert {'message': "Game has already started."} == load(response)
