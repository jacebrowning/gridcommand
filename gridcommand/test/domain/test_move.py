"""Unit tests for the `domain.move` module."""
# pylint: disable=R0201,C0103,C0111,misplaced-comparison-constant

from gridcommand.domain import Move


class TestMove:

    def test_init(self):
        move = Move(1, 2)  # TODO: create fixture
        assert 1 == move.begin
        assert 2 == move.end
        assert 0 == move.count

    def test_repr(self):
        move = Move(1, 2)  # TODO: create fixture
        assert "<move: 0 from 1 to 2>" == repr(move)

    def test_eq_if_begin_and_end_both_match(self):
        assert Move(1, 2) == Move(1, 2)

    def test_eq_ignores_count(self):
        assert Move(1, 2) == Move(1, 2, 99)

    def test_ne_if_begin_or_end_different(self):
        assert Move(1, 2) != Move(1, 3)
        assert Move(1, 2) != Move(4, 2)
        assert Move(1, 2) != Move(5, 5)

    def test_lt_if_begin_is_less(self):
        assert Move(1, 1) < Move(2, 1)

    def test_lt_if_begin_eq_and_end_less(self):
        assert Move(1, 1) < Move(1, 2)

    def test_sort(self):
        moves = [Move(1, 2), Move(1, 5), Move(2, 3), Move(3, 4)]
        assert moves == sorted(moves)
