"""Unit tests for the `models` module."""
# pylint: disable=R0201

from gridcommand.models import Move


class TestMove:

    def test_init_count_eq_zero(self):
        move = Move(1, 2)
        assert 1 == move.begin
        assert 2 == move.end
        assert 0 == move.count

    def test_eq_if_begin_and_end_both_match(self):
        assert Move(1, 2) == Move(1, 2)
        assert Move(1, 2) != Move(1, 3)
        assert Move(1, 2) != Move(4, 2)
        assert Move(1, 2) != Move(5, 5)
        assert Move(1, 2) == Move(1, 2, 99)
