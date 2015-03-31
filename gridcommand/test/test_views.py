# pytest: disable=C0103

from .conftest import load


def test_index_returns_version_and_games_url(client):
    response = client.get('/')
    assert 200 == response.status_code
    assert {'version': 1,
            'games': "http://localhost/games/"} == load(response)
