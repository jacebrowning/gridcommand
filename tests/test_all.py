"""Unit tests for the `views.game` module."""
# pylint: disable=W0613,R0201,C0103,C0111


from .conftest import load


def test_create_game_and_players(client):

    # Create a game

    response = client.post('/api/games/')
    assert 201 == response.status_code
    game_url = load(response)['uri']

    response = client.get(game_url)
    assert 200 == response.status_code
    players_url = load(response)['players']

    # Create two players

    response = client.post(players_url, data={'code': '1'})
    assert 201 == response.status_code
    player1_url = load(response)['uri']
    response = client.post(players_url, data={'code': '2'})
    assert 201 == response.status_code
    player2_url = load(response)['uri']
