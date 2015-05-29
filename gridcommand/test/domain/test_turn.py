"""Unit tests for the `domain.turn` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.domain import Turns


class TestTurn:

    def test_init(self, turn):
        assert not turn.done
        assert not turn.moves

    def test_repr(self, turn):
        assert "<turn>" == repr(turn)


class TestTurns:

    def test_repr(self, turns):
        assert "<2 turns>" == repr(turns)
        turns.pop()
        assert "<1 turn>" == repr(turns)

    def test_current(self, turns):
        assert turns.current

    def test_current_none(self):
        assert None is Turns().current

    def test_find_match(self, turns):
        turns.find(1)

    def test_find_missing(self, player):
        with pytest.raises(ValueError):
            player.turns.find(1)
