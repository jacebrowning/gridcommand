from unittest.mock import patch

from expecter import expect

from app.enums import Color
from app.models import Board, Cell


def fixed_roll(count: int):
    rolls = {
        1: [1],
        2: [2, 2],
        3: [3, 3, 3],
        4: [4, 4, 4, 4],
        5: [5, 5, 5, 5, 5],
        6: [6, 6, 6, 6, 6, 6],
    }
    return rolls[count]


def describe_fortifications():
    def single_fortification():
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

    def mass_fortification():
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


def describe_marchs():
    def single_march():
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

    def mass_march():
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


def describe_attacks():
    def losing_mass_attack():
        board = Board()
        board.cells = [
            Cell(0, 0, Color.BLUE, 0, right=1),
            Cell(0, 1, Color.RED, 2),
            Cell(0, 2, Color.BLUE, 1, left=1),
        ]

        with patch("app.actions.roll", fixed_roll):
            board.advance()

        expect(board.cells) == [
            Cell(0, 0, Color.NONE, 0),
            Cell(0, 1, Color.RED, 2),
            Cell(0, 2, Color.BLUE, 1),
        ]

    def winning_mass_attack():
        board = Board()
        board.cells = [
            Cell(0, 0, Color.BLUE, 0, right=1),
            Cell(0, 1, Color.RED, 2),
            Cell(0, 2, Color.BLUE, 0, left=3),
        ]

        with patch("app.actions.roll", fixed_roll):
            board.advance()

        expect(board.cells) == [
            Cell(0, 0, Color.NONE, 0),
            Cell(0, 1, Color.BLUE, 4),
            Cell(0, 2, Color.NONE, 0),
        ]
