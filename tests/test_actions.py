from expecter import expect

from app.enums import Color
from app.models import Board, Cell


def describe_fortification():
    def when_single():
        board = Board()
        board.cells = [
            Cell(0, 0, Color.BLUE, 1, right=1),
            Cell(0, 1, Color.BLUE, 1),
        ]

        board.advance()

        expect(board.cells) == [
            Cell(0, 0, Color.BLUE, 1),
            Cell(0, 1, Color.BLUE, 2),
        ]

    def when_mass():
        board = Board()
        board.cells = [
            Cell(0, 0, Color.BLUE, 1, right=1),
            Cell(0, 1, Color.BLUE, 1),
            Cell(0, 2, Color.BLUE, 1, left=1),
        ]

        board.advance()

        expect(board.cells) == [
            Cell(0, 0, Color.BLUE, 1),
            Cell(0, 1, Color.BLUE, 3),
            Cell(0, 2, Color.BLUE, 1),
        ]


def describe_march():
    def when_single():
        board = Board()
        board.cells = [
            Cell(0, 0, Color.BLUE, 1, right=1),
            Cell(0, 1, Color.NONE, 0),
        ]

        board.advance()

        expect(board.cells) == [
            Cell(0, 0, Color.BLUE, 1),
            Cell(0, 1, Color.BLUE, 1),
        ]

    def when_mass():
        board = Board()
        board.cells = [
            Cell(0, 0, Color.BLUE, 1, right=1),
            Cell(0, 1, Color.NONE, 0),
            Cell(0, 2, Color.BLUE, 1, left=1),
        ]

        board.advance()

        expect(board.cells) == [
            Cell(0, 0, Color.BLUE, 1),
            Cell(0, 1, Color.BLUE, 2),
            Cell(0, 2, Color.BLUE, 1),
        ]
