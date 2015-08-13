"""Unit tests for the `domain.turn` module."""
# pylint: disable=R0201,C0103,C0111


class TestTurn:

    def test_init(self, turn):
        assert not turn.done
        assert not turn.moves

    def test_repr(self, turn):
        assert "<turn: not done>" == repr(turn)
