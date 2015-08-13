"""Unit tests for the `domain.game` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.domain import Game


class TestGame:

    def test_repr(self, game):
        assert "<game: my_game>" == repr(game)

    def test_eq(self):
        game1 = Game('abc123')
        game2 = Game('abc123')
        game3 = Game('def456')
        assert game1 == game2
        assert game1 != game3

    def test_start_triggers_turn_1(self, game_players):
        assert 0 == game_players.turn
        game_players.start()
        assert 1 == game_players.turn

    def test_start_again_raises_exception(self, game_started):
        assert 1 == game_started.turn
        with pytest.raises(ValueError):
            game_started.start()
        assert 1 == game_started.turn

    def test_advance_triggers_next_turn(self, game_started):
        assert 1 == game_started.turn
        game_started.advance()
        assert 2 == game_started.turn
        game_started.advance()
        assert 3 == game_started.turn

    def test_error_creating_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.create_player('1234')

    def test_error_deleting_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.delete_player('red')
