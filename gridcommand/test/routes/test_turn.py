"""Unit tests for the `views.turn` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES, EXTERNAL


TURNS = GAMES + "my_game/players/red/turns/"


class TestTurns:

    def test_get_all_turns(self, client, turn):
        response = client.get(TURNS + "?code=my_code")
        assert 200 == response.status_code
        assert [
            EXTERNAL + TURNS + "1?code=my_code",
        ] == load(response)


class TestTurn:

    def test_get_existing_turn(self, client, turn):
        response = client.get(TURNS + "1?code=my_code")
        assert 200 == response.status_code
        assert {
            'uri': EXTERNAL + TURNS + "1?code=my_code",
            'moves': EXTERNAL + TURNS + "1/moves/?code=my_code",
            'finish': EXTERNAL + TURNS + "1/finish?code=my_code"
        } == load(response)


class TestTurnFinish:

    def test_get_started(self, client, turn):
        response = client.get(TURNS + "1/finish?code=my_code")
        assert 200 == response.status_code
        assert {'finished': False} == load(response)

    def test_get_finished(self, client, turn_completed):
        response = client.get(TURNS + "1/finish?code=my_code")
        assert 200 == response.status_code
        assert {'finished': True} == load(response)

    def test_post_finish_turn(self, client, turn):
        response = client.post(TURNS + "1/finish?code=my_code")
        assert 200 == response.status_code
        assert {'finished': True} == load(response)

    def test_post_finish_turn_already_finished(self, client, turn_completed):
        response = client.post(TURNS + "1/finish?code=my_code")
        assert 403 == response.status_code
        assert {
            'message': "The turn has already finished.",
        } == load(response)
