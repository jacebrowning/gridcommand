"""Unit tests for the `views.game` module."""
# pylint: disable=W0613,R0201,C0103,C0111


from .conftest import load


def test_create_game(client):

    response = client.post('/api/games/')
    assert 201 == response.status_code
    url = load(response)['uri']

    response = client.get(url)
    assert 200 == response.status_code
