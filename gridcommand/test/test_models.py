"""Unit tests for the `models` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.models import Move, Player, Players, Games


class TestMove:

    def test_init_count_to_zero(self):
        move = Move(1, 2)
        assert 1 == move.begin
        assert 2 == move.end
        assert 0 == move.count

    def test_eq_if_begin_and_end_both_match(self):
        assert Move(1, 2) == Move(1, 2)

    def test_eq_ignores_count(self):
        assert Move(1, 2) == Move(1, 2, 99)

    def test_ne_if_begin_or_end_different(self):
        assert Move(1, 2) != Move(1, 3)
        assert Move(1, 2) != Move(4, 2)
        assert Move(1, 2) != Move(5, 5)


class TestPlayer:

    def test_eq_if_colors_match(self):
        player1 = Player('red')
        player2 = Player('red')
        player3 = Player('blue')
        assert player1 == player2
        assert player1 != player3


class TestPlayers:

    def test_create_unique_colors(self):
        players = Players()
        player1 = players.create()
        player2 = players.create()
        assert player1.color != player2.color

    def test_create_maximum_players(self):
        players = Players()
        with pytest.raises(RuntimeError):
            for _ in range(999):
                players.create()
        assert 8 == len(players)

    def test_create_reuse_after_removal(self):
        players = Players()
        player1 = players.create()
        players.remove(player1)
        player2 = players.create()
        assert player1 == player2

    def test_find_match(self):
        players = Players()
        player = players.create()
        player2 = players.find(player.color)
        assert player is player2

    def test_find_missing(self):
        players = Players()
        with pytest.raises(ValueError):
            players.find('red')

    def test_delete(self):
        players = Players()
        player = players.create()
        assert player in players
        players.delete(player.color)
        assert player not in players


class TestGames:

    def test_find_match(self):
        games = Games()
        game = games.create()
        game2 = games.find(game.key)
        assert game is game2

    def test_find_missing(self):
        games = Games()
        with pytest.raises(ValueError):
            games.find('abc123')
