"""Unit tests for the `views.turn` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES


TURNS = GAMES + "my_game/players/red/turns/"


class TestTurns:

    def test_get_all_turns(self, client, turn):
        response = client.get('/api/games/'
                              'my_game/players/red/turns/?code=my_code')
        assert 200 == response.status_code
        assert load(response) == [
            GAMES + "my_game/players/red/turns/1?code=my_code",
        ]


class TestTurn:

    def test_get_existing_turn(self, client, turn):
        response = client.get('/api/games/'
                              'my_game/players/red/turns/1?code=my_code')
        assert 200 == response.status_code
        assert {'uri': TURNS + "1?code=my_code",
                'moves': TURNS + "1/moves/?code=my_code",
                'done': False} == load(response)
