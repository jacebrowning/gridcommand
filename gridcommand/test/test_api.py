"""Unit tests for the `views` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from unittest.mock import patch, Mock

from .conftest import load

GAMES = "http://localhost/api/games/"


class TestIndex:

    def test_redirect(self, client):
        response = client.get('/')
        assert 302 == response.status_code


class TestRoot:

    def test_version(self, client):
        response = client.get('/api/')
        assert 200 == response.status_code
        assert {'version': 1,
                'games': GAMES} == load(response)


class TestGames:

    def test_get_games_list_hidden(self, client):
        response = client.get('/api/games/')
        assert 403 == response.status_code
        assert {'message':
                "Games list is hidden."} == load(response)

    @patch('gridcommand.models.Game._generate_key', Mock(return_value='x'))
    def test_post_new_game(self, client):
        response = client.post('/api/games/')
        assert 201 == response.status_code
        assert {'key': "x",
                'players': GAMES + "x/players/",
                'start': GAMES + "x/start",
                'phase': 0} == load(response)


class TestGame:

    def test_get_existing_game(self, client, game):
        response = client.get('/api/games/my_game/')
        assert 200 == response.status_code
        assert {'key': "my_game",
                'players': GAMES + "my_game/players/",
                'start': GAMES + "my_game/start",
                'phase': 0} == load(response)

    def test_get_missing_game(self, client):
        response = client.get('/api/games/my_game/')
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


class TestPlayers:

    def test_get_players(self, client, game_players):
        response = client.get('/api/games/my_game/players/')
        assert 200 == response.status_code
        assert [GAMES + "my_game/players/red/",
                GAMES + "my_game/players/blue/"] == load(response)

    def test_post_player(self, client, game):
        response = client.post('/api/games/my_game/players/',
                               data={'code': "1234"})
        assert 201 == response.status_code
        assert {'color': "red",
                'code': '1234',
                'phases': GAMES + "my_game/players/red/1234/phases/",
                'phase': 0} == load(response)

    def test_post_player_with_invalid_coe(self, client, game):
        response = client.post('/api/games/my_game/players/')
        assert 400 == response.status_code
        assert {'message':
                "Player 'code' must be specified."} == load(response)


class TestPlayer:

    def test_get_existing_player(self, client, player):
        response = client.get('/api/games/my_game/players/red/')
        assert 200 == response.status_code
        assert {'color': "red",
                'phase': 0} == load(response)

    def test_get_existing_player_with_auth(self, client, player):
        response = client.get('/api/games/my_game/players/red/my_code/')
        assert 200 == response.status_code
        assert {'color': "red",
                'code': 'my_code',
                'phases': GAMES + "my_game/players/red/my_code/phases/",
                'phase': 0} == load(response)

    def test_get_existing_player_bad_auth(self, client, player):
        response = client.get('/api/games/my_game/players/red/invalid/')
        assert 401 == response.status_code
        assert {'message': "The code 'invalid' is invalid."}

    def test_get_missing_player(self, client, game):
        response = client.get('/api/games/my_game/players/red/')
        assert 404 == response.status_code
        assert {'message':
                "The player 'red' does not exist."} == load(response)

    def test_put_new_code(self, client, player):
        response = client.put('/api/games/my_game/players/red/my_code/',
                              data={'code': "1234"})
        assert 200 == response.status_code
        assert {'color': "red",
                'code': '1234',
                'phases': GAMES + "my_game/players/red/1234/phases/",
                'phase': 0} == load(response)


class TestPhases:

    def test_get_all_phases(self, client, phase):
        response = client.get('/api/games/my_game/players/red/my_code/phases/')
        assert 200 == response.status_code


class TestPhase:

    def test_get_existing_phase(self, client, phase):
        response = client.get('/api/games/'
                              'my_game/players/red/my_code/phases/1/')
        assert 200 == response.status_code
        assert {'moves': GAMES + "my_game/players/red/my_code/phases/1/moves/",
                'done': False} == load(response)
