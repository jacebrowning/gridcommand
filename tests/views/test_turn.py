"""Unit tests for the `api.turn` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES


class TestTurns:

    def test_get_all_turns(self, client, turn):
        response = client.get('/api/games/my_game/players/red-my_code/turns/')
        assert 200 == response.status_code
        # TODO: check loaded response


class TestTurn:

    def test_get_existing_turn(self, client, turn):
        response = client.get('/api/games/'
                              'my_game/players/red-my_code/turns/1')
        assert 200 == response.status_code
        assert {'uri': GAMES + "my_game/players/red-my_code/turns/1",
                'moves': GAMES + "my_game/players/red-my_code/turns/1/moves/",
                'done': False} == load(response)
