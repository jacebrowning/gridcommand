"""Unit tests for the `views.root` module."""
# pylint: disable=W0613,R0201,C0103,C0111

from ..conftest import load

from . import GAMES, EXTERNAL


class TestIndex:

    def test_redirect(self, client):
        response = client.get('/')
        assert 302 == response.status_code


class TestRoot:

    def test_version(self, client):
        response = client.get('/api')
        assert 200 == response.status_code
        assert {
            'version': 1,
            'games': EXTERNAL + GAMES,
        } == load(response)
