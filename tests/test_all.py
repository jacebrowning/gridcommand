"""Unit tests for the `views.game` module."""
# pylint: disable=W0613,R0201,C0103,C0111


from .conftest import load


def test_create_game_and_players(client):

    # Attempt to get the games list

    response = client.get('/api/games/')
    assert 403 == response.status_code

    # Create a game

    response = client.post('/api/games/')
    assert 201 == response.status_code
    game_url = load(response)['uri']
    game_start_url = load(response)['start']

    response = client.get(game_url)
    assert 200 == response.status_code
    players_url = load(response)['players']

    # Attempt to start without players

    response = client.get(game_start_url)
    assert False is load(response)['started']

    response = client.post(game_start_url)
    assert 403 == response.status_code

    # Create two players

    response = client.post(players_url, data={'code': '1'})
    assert 201 == response.status_code
    player_1_url = load(response)['uri']
    response = client.post(players_url, data={'code': '2'})
    assert 201 == response.status_code
    player_2_url = load(response)['uri']

    response = client.get(player_1_url)
    assert 200 == response.status_code
    turn = load(response)['turn']

    # Start the game



