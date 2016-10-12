# pylint: disable=no-self-use
# pylint: disable=misplaced-comparison-constant

import pytest

from gridcommand.domain import Player, Players


class TestPlayer:

    def test_repr(self, player):
        assert "<player: red>" == repr(player)

    def test_eq_if_colors_match(self):
        assert Player('red') == Player('red')
        assert Player('red') != Player('blue')

    def test_authentication(self, player):
        player.authenticate('my_code')
        with pytest.raises(ValueError):
            player.authenticate('invalid')


class TestPlayers:

    def test_repr(self, players):
        assert "<2 players>" == repr(players)
        players.pop()
        assert "<1 player>" == repr(players)

    def test_create_unique_colors(self):
        players = Players()
        player1 = players.create('abc')
        player2 = players.create('123')
        assert player1.color != player2.color

    def test_create_maximum_players(self):
        players = Players()
        for _ in range(8):
            players.create()
        with pytest.raises(RuntimeError):
            players.create()

    def test_create_reuse_after_delete(self, players):
        players.delete('blue')
        player = players.create('1234')
        assert 'blue' == player.color

    def test_find_match(self, players):
        player = players.find('blue')
        assert 'blue' == player.color

    def test_find_missing(self):
        players = Players()
        with pytest.raises(ValueError):
            players.find('red')

    def test_delete(self, players):
        player = players.find('blue')
        assert player in players
        players.delete('blue')
        assert player not in players

    def test_delete_missing(self, players):
        players.delete('not-a-color')
