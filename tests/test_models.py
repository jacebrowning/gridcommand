import pytest

from app.enums import Color
from app.models import Cell, Game


@pytest.fixture
def game():
    g = Game()
    g.initialize(1)
    g.board.cells = [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 2),
        Cell(0, 2, Color.NONE, 0),
        Cell(0, 3, Color.BLUE, 3),
        Cell(0, 4, Color.BLUE, 1),
        Cell(0, 5, Color.BLUE, 1),
        Cell(0, 6, Color.BLUE, 1),
    ]
    return g


def test_fortify(game):
    game.advance()
    assert game.board.cells == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 3),
        Cell(0, 2, Color.NONE, 0),
        Cell(0, 3, Color.BLUE, 4),
        Cell(0, 4, Color.BLUE, 1),
        Cell(0, 5, Color.BLUE, 1),
        Cell(0, 6, Color.BLUE, 1),
    ]
