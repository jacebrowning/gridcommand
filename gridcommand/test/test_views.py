"""Unit tests for the `views` module."""
# pylint: disable=R0201,C0103

from gridcommand import models, views

from .conftest import load


class TestIndex:

    def test_version(self, client):
        response = client.get('/')

        assert 200 == response.status_code
        assert {'version': 1,
                'games': "http://localhost/games/"} == load(response)


class TestGames:

    def test_get_existing_game(self, client):
        game = models.Game('my_game')
        views.games[game.key] = game

        response = client.get('/games/my_game/')

        assert 200 == response.status_code
        assert {'players': "http://localhost/games/my_game/players/",
                'started': False} == load(response)

    def test_get_missing_game(self, client):
        response = client.get('/games/my_game/')

        assert 404 == response.status_code
        assert {'message':
                "The game 'my_game' does not exist."} == load(response)


class TestPlayers:

    def test_get_missing_player(self, client):
        game = models.Game('my_game')
        views.games[game.key] = game

        response = client.get('/games/my_game/players/red/')

        assert 404 == response.status_code
        assert {'message':
                "The player 'red' does not exist."} == load(response)
