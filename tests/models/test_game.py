"""Unit tests for the `models.game` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.models.game import Games


class TestGame:

    def test_start_triggers_phase_1(self, game_players):
        assert 0 == game_players.phase
        game_players.start()
        assert 1 == game_players.phase

    def test_create_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.create_player('1234')

    def test_delete_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.delete_player('red')


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
