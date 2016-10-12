# pylint: disable=no-self-use

import pytest


class TestGameService:

    def test_find_match(self, game_service):
        game = game_service.create_game()
        game2 = game_service.find_game(game.key)
        assert game is game2

    def test_find_missing(self, game_service):
        with pytest.raises(KeyError):
            game_service.find_game('abc123')
