"""Unit tests for the `views` module."""
# pylint: disable=W0613,R0201,C0103,C0111

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


class TestGame:

    def test_get_existing_game(self, client, my_game):
        response = client.get('/api/games/my_game/')
        assert 200 == response.status_code
        assert {'players': GAMES + "my_game/players/",
                'round': 0,
                'started': False} == load(response)

    def test_get_missing_game(self, client):
        response = client.get('/api/games/my_game/')
        assert 404 == response.status_code
        assert {'message':
                "The game 'my_game' does not exist."} == load(response)


class TestPlayers:

    def test_post_player(self, client, my_game):
        response = client.post('/api/games/my_game/players/',
                               data={'code': "1234"})
        assert 201 == response.status_code
        assert {'color': "red",
                'code': '1234',
                'rounds': GAMES + "my_game/players/red/1234/rounds/",
                'round': 0} == load(response)

    def test_post_player_with_invalid_coe(self, client, my_game):
        response = client.post('/api/games/my_game/players/')
        assert 400 == response.status_code
        assert {'message':
                "Player 'code' must be specified."} == load(response)


class TestPlayer:

    def test_get_existing_player(self, client, my_player):
        response = client.get('/api/games/my_game/players/red/')
        assert 200 == response.status_code
        assert {'color': "red",
                'round': 0} == load(response)

    def test_get_existing_player_with_auth(self, client, my_player):
        response = client.get('/api/games/my_game/players/red/my_code/')
        assert 200 == response.status_code
        assert {'color': "red",
                'code': 'my_code',
                'rounds': GAMES + "my_game/players/red/my_code/rounds/",
                'round': 0} == load(response)

    def test_get_existing_player_bad_auth(self, client, my_player):
        response = client.get('/api/games/my_game/players/red/invalid/')
        assert 401 == response.status_code
        assert {'message': "The code 'invalid' is invalid."}

    def test_get_missing_player(self, client, my_game):
        response = client.get('/api/games/my_game/players/red/')
        assert 404 == response.status_code
        assert {'message':
                "The player 'red' does not exist."} == load(response)

    def test_put_new_code(self, client, my_player):
        response = client.put('/api/games/my_game/players/red/my_code/',
                              data={'code': "1234"})
        assert 200 == response.status_code
        assert {'color': "red",
                'code': '1234',
                'rounds': GAMES + "my_game/players/red/1234/rounds/",
                'round': 0} == load(response)


class TestRounds:

    def test_get_all_rounds(self, client, my_round):
        response = client.get('/api/games/my_game/players/red/my_code/rounds/')
        assert 200 == response.status_code


class TestRound:

    def test_get_existing_round(self, client, my_round):
        response = client.get('/api/games/'
                              'my_game/players/red/my_code/rounds/1/')
        assert 200 == response.status_code
        assert {'moves': GAMES + "my_game/players/red/my_code/rounds/1/moves/",
                'done': False} == load(response)
