# pylint: disable=no-self-use
# pylint: disable=unused-argument,misplaced-comparison-constant

from ..utils import load

from . import GAMES, EXTERNAL


EXTERNAL_GAMES = EXTERNAL + GAMES


class TestPlayers:

    PLAYERS = GAMES + "my_game/players/"

    def test_get_players(self, client, game_players):
        response = client.get(self.PLAYERS)
        assert 200 == response.status_code
        assert [
            EXTERNAL_GAMES + "my_game/players/red",
            EXTERNAL_GAMES + "my_game/players/blue",
        ] == load(response)

    def test_post_player(self, client, game):
        response = client.post(self.PLAYERS,
                               data={'code': "1234"})
        assert 201 == response.status_code
        assert {
            'uri': EXTERNAL_GAMES + "my_game/players/red?code=1234",
            'color': "red",
            'code': "1234",
            'done': False,
            'turns': EXTERNAL_GAMES + "my_game/players/red/turns/?code=1234",
        } == load(response)

    def test_post_player_with_invalid_code(self, client, game):
        response = client.post(self.PLAYERS)
        assert 400 == response.status_code
        assert {
            'message': "Player 'code' must be specified.",
        } == load(response)

    def test_post_player_after_game_start(self, client, game_started):
        response = client.post(self.PLAYERS,
                               data={'code': "1234"})
        assert 403 == response.status_code
        assert {
            'message': "Game has already started.",
        } == load(response)


class TestPlayer:

    PLAYER = TestPlayers.PLAYERS + "red"

    def test_get_existing_player(self, client, player):
        response = client.get(self.PLAYER)
        assert 200 == response.status_code
        assert {
            'uri': EXTERNAL_GAMES + "my_game/players/red",
            'color': "red",
            'done': False,
        } == load(response)

    def test_get_missing_player(self, client, game):
        response = client.get(self.PLAYER)
        assert 404 == response.status_code
        assert {
            'message': "The player 'red' does not exist.",
        } == load(response)

    def test_delete_player(self, client, player):
        response = client.delete(self.PLAYER)
        assert 401 == response.status_code
        assert {
            'message': "Player code required.",
        } == load(response)


class TestPlayerWithAuth:

    AUTH = TestPlayer.PLAYER + "?code=my_code"

    def test_get_existing_player(self, client, player):
        response = client.get(self.AUTH)
        assert 200 == response.status_code
        assert {
            'uri': EXTERNAL_GAMES + "my_game/players/red?code=my_code",
            'color': "red",
            'code': "my_code",
            'done': False,
            'turns': EXTERNAL_GAMES + "my_game/players/red/turns/?code=my_code",
        } == load(response)

    def test_get_existing_player_with_bad_auth(self, client, player):
        response = client.get(TestPlayer.PLAYER + "?code=invalid")
        assert 401 == response.status_code
        assert {
            'message': "Player code 'invalid' is invalid.",
        } == load(response)

    def test_delete_player(self, client, player):
        response = client.delete(self.AUTH)
        assert 204 == response.status_code
        assert None is load(response)

    def test_delete_player_after_game_start(self, client, game_started):
        response = client.delete(self.AUTH)
        assert 403 == response.status_code
        assert {
            'message': "Game has already started.",
        } == load(response)
