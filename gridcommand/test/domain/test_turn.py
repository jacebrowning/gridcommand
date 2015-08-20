"""Unit tests for the `domain.turn` module."""
# pylint: disable=R0201,C0103,C0111

import pytest


class TestTurn:

    def test_init(self, turn):
        assert not turn.done
        assert not turn.moves

    def test_repr(self, turn):
        assert "<turn: started>" == repr(turn)

    def test_repr_completed(self, turn_completed):
        assert "<turn: finished>" == repr(turn_completed)

    def test_finish(self, turn):
        assert False is turn.done
        turn.finish()
        assert True is turn.done

    def test_error_finishing_twice(self, turn_completed):
        with pytest.raises(ValueError):
            turn_completed.finish()
        assert True is turn_completed.done
