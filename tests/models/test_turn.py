"""Unit tests for the `models.turn` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.models.turn import Turns


class TestTurn:

    def test_init(self, turn):
        assert not turn.done
        assert not turn.moves


class TestTurns:

    def test_current(self, turns):
        assert turns.current

    def test_current_none(self):
        assert None is Turns().current

    def test_find_match(self, turns):
        turns.find(1)

    def test_find_missing(self, player):
        with pytest.raises(ValueError):
            player.turns.find(1)
