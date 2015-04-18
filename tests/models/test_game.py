"""Unit tests for the `models.game` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.models.game import Games


class TestGame:

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
