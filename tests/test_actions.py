import pytest

from app.enums import Color
from app.models import Board, Cell


@pytest.mark.xfail
def test_mass_fortification():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 0),
        Cell(0, 2, Color.BLUE, 1),
    ]

    for move in board.fortifications:
        move.perform()

    assert board.cells == [
        Cell(0, 0, Color.BLUE, 0),
        Cell(0, 1, Color.BLUE, 2),
        Cell(0, 2, Color.BLUE, 0),
    ]
