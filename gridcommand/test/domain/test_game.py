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

    def test_start_adds_turn_to_players(self, game_players):
        assert 0 == len(game_players.players[0].turns)
        game_players.start()
        assert 1 == len(game_players.players[0].turns)

    def test_start_again_does_nothing(self, game_started):
        assert 1 == game_started.turn
        game_started.start()
        assert 1 == game_started.turn

    def test_create_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.create_player('1234')

    def test_delete_player_after_start(self, game_started):
        with pytest.raises(ValueError):
            game_started.delete_player('red')

    def test_advance_ends_current_turn(self, game_started):
        assert False is game_started.players[0].turns[0].done
        assert False is game_started.players[1].turns[0].done
        game_started.advance()
        assert True is game_started.players[0].turns[0].done
        assert True is game_started.players[1].turns[0].done

    def test_advance_adds_turn(self, game_started):
        assert 1 == len(game_started.players[0].turns)
        assert 1 == len(game_started.players[1].turns)
        game_started.advance()
        assert 2 == len(game_started.players[0].turns)
        assert 2 == len(game_started.players[1].turns)