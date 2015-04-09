"""Unit tests for the `api.phase` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES


class TestPhases:

    def test_get_all_phases(self, client, phase):
        response = client.get('/api/games/my_game/players/red-my_code/phases/')
        assert 200 == response.status_code


class TestPhase:

    def test_get_existing_phase(self, client, phase):
        response = client.get('/api/games/'
                              'my_game/players/red-my_code/phases/1')
        assert 200 == response.status_code
        assert {'moves': GAMES + "my_game/players/red-my_code/phases/1/moves/",
                'done': False} == load(response)
