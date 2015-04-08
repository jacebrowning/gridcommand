"""Unit tests for the `models` module."""
# pylint: disable=R0201,C0103,C0111

from unittest.mock import Mock

import pytest

from gridcommand.models import Move
from gridcommand.models import Player, Players
from gridcommand.models import Games


class TestMove:

    def test_init(self):
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

    def test_lt_if_begin_is_less(self):
        assert Move(1, 1) < Move(2, 1)

    def test_lt_if_begin_eq_and_end_less(self):
        assert Move(1, 1) < Move(1, 2)

    def test_sort(self):
        moves = [Move(1, 2), Move(1, 5), Move(2, 3), Move(3, 4)]
        assert moves == sorted(moves)


class TestPhase:

    def test_init(self, phase):
        assert False is phase.done
        assert not len(phase.moves)


class TestPhases:

    def test_find_match(self, phases):
        phases.append(Mock())
        phases.find(1)

    def test_find_missing(self, phases):
        with pytest.raises(ValueError):
            phases.find(1)


class TestPlayer:

    def test_eq_if_colors_match(self):
        assert Player('red') == Player('red')
        assert Player('red') != Player('blue')

    def test_authentication(self, player):
        player.authenticate('my_code')
        with pytest.raises(ValueError):
            player.authenticate('invalid')


class TestPlayers:

    def test_create_unique_colors(self):
        players = Players()
        player1 = players.create('abc')
        player2 = players.create('123')
        assert player1.color != player2.color

    def test_create_maximum_players(self):
        players = Players()
        with pytest.raises(RuntimeError):
            for _ in range(999):
                players.create()
        assert 8 == len(players)

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


class TestGame:

    def test_start_triggers_phase_1(self, game_players):
        assert 0 == game_players.phase
        game_players.start()
        assert 1 == game_players.phase

    def test_create_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.create_player('1234')


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
