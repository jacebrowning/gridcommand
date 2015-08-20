"""Unit tests for the `views.move` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES


MOVES = GAMES + "my_game/players/red/turns/1/moves/"


class TestMoves:

    def test_get_all_moves(self, client, turn):
        response = client.get(MOVES + "?code=my_code")
        assert 200 == response.status_code
        assert [
        ] == load(response)
