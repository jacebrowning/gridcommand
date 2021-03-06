# pylint: disable=no-self-use
# pylint: disable=misplaced-comparison-constant

from ..utils import load

from . import GAMES, EXTERNAL


class TestRoot:

    def test_version(self, client):
        response = client.get('/api')
        assert 200 == response.status_code
        assert {
            'version': 1,
            'games': EXTERNAL + GAMES,
        } == load(response)
