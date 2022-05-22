from unittest.mock import Mock, patch

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


def test_fortification_with_1_cell():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 1, right=1),
        Cell(0, 1, Color.BLUE, 1),
    ]

    assert board.advance() == 1

    expect(board.cells) == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 2),
    ]


def test_fortification_with_2_cells():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 1, right=1),
        Cell(0, 1, Color.BLUE, 1),
        Cell(0, 2, Color.BLUE, 1, left=1),
    ]

    assert board.advance() == 2

    expect(board.cells) == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 3),
        Cell(0, 2, Color.BLUE, 1),
    ]


def test_march_with_1_cell():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 1, right=1),
        Cell(0, 1, Color.NONE, 0),
    ]

    assert board.advance() == 1

    expect(board.cells) == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 1),
    ]


def test_march_with_2_cells():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 1, right=1),
        Cell(0, 1, Color.NONE, 0),
        Cell(0, 2, Color.BLUE, 1, left=1),
    ]

    assert board.advance() == 2

    expect(board.cells) == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 2),
        Cell(0, 2, Color.BLUE, 1),
    ]


def test_2_attacks_in_sequence():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 1, right=2),
        Cell(0, 1, Color.RED, 1, right=2),
        Cell(0, 2, Color.GREEN, 1),
    ]

    with patch("app.actions.roll", fixed_roll):
        assert board.advance() == 2

    expect(board.cells) == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(
            0,
            1,
            Color.BLUE,
            2,
        ),
        Cell(0, 2, Color.RED, 2),
    ]


def test_mass_attack_with_2_cells_and_win():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 0, right=1),
        Cell(0, 1, Color.RED, 2),
        Cell(0, 2, Color.BLUE, 1, left=1),
    ]

    with patch("app.actions.roll", fixed_roll):
        assert board.advance() == 1

    expect(board.cells) == [
        Cell(0, 0, Color.NONE, 0),
        Cell(0, 1, Color.RED, 2),
        Cell(0, 2, Color.BLUE, 1),
    ]


def test_mass_attack_with_2_cells_and_retreating_enemy():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 0, right=1),
        Cell(0, 1, Color.RED, 1, down=1),
        Cell(0, 2, Color.BLUE, 0, left=1),
        Cell(1, 1, Color.NONE, 0),
    ]

    with patch("app.actions.roll", fixed_roll):
        assert board.advance() == 4

    expect(board.cells) == [
        Cell(0, 0, Color.NONE, 0),
        Cell(0, 1, Color.BLUE, 2),
        Cell(0, 2, Color.NONE, 0),
        Cell(1, 1, Color.RED, 1),
    ]


def test_mass_attack_with_2_cells_and_loss():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 0, right=1),
        Cell(0, 1, Color.RED, 2),
        Cell(0, 2, Color.BLUE, 0, left=3),
    ]

    with patch(
        "app.actions.roll",
        Mock(side_effect=[[6, 1, 1, 1], [3, 3], [6, 1, 1], [3], [6, 1], [3]]),
    ):
        assert board.advance() == 2

    expect(board.cells) == [
        Cell(0, 0, Color.NONE, 0),
        Cell(0, 1, Color.BLUE, 3),
        Cell(0, 2, Color.NONE, 0),
    ]


def test_spoils_of_war_with_2_cells():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 0, right=2),
        Cell(0, 1, Color.NONE, 0),
        Cell(0, 2, Color.RED, 1, left=1),
    ]

    with patch("app.actions.roll", fixed_roll):
        assert board.advance() == 2

    expect(board.cells) == [
        Cell(0, 0, Color.NONE, 0),
        Cell(0, 1, Color.BLUE, 2),
        Cell(0, 2, Color.RED, 1),
    ]


def test_spoils_of_war_with_3_cells():
    board = Board()
    board.cells = [
        Cell(0, 0, Color.BLUE, 0, right=2),
        Cell(0, 1, Color.RED, 1),
        Cell(0, 2, Color.GREEN, 0, left=2),
    ]

    with patch("app.actions.roll", fixed_roll):
        assert board.advance() == 3

    expect(board.cells) == [
        Cell(0, 0, Color.NONE, 0),
        Cell(0, 1, Color.BLUE, 2),
        Cell(0, 2, Color.NONE, 0),
    ]
