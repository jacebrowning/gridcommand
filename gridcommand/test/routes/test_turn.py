"""Unit tests for the `views.turn` module."""
# pylint: disable=W0613,R0201,C0103,C0111,misplaced-comparison-constant

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

    def test_get_past_turn(self, client, game_turns):
        response = client.get(TURNS + "1?code=my_code")
        assert 403 == response.status_code
        assert {
            'message': "This turn is in the past."
        } == load(response)

    def test_get_current_turn(self, client, game_turns):
        response = client.get(TURNS + "2?code=my_code")
        assert 200 == response.status_code
        assert {
            'uri': EXTERNAL + TURNS + "2?code=my_code",
            'moves': EXTERNAL + TURNS + "2/moves/?code=my_code",
            'finish': EXTERNAL + TURNS + "2/finish?code=my_code"
        } == load(response)

    def test_get_future_turn(self, client, game_turns):
        response = client.get(TURNS + "3?code=my_code")
        assert 404 == response.status_code
        assert {
            'message': "This turn is in the future."
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
