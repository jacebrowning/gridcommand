import random

from expecter import expect

from app import autoplay
from app.enums import Color, State
from app.types import Cell, Player


def test_plan_moves_units_with_board_context():
    cells = [
        Cell(0, 0, Color.RED, 3, size=2),
        Cell(0, 1, Color.NONE, 0, size=2),
        Cell(1, 0, Color.NONE, 0, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    random.seed(0)
    moved = autoplay.plan([cells[0]], player, board=cells)

    cell = cells[0]
    expect(moved) > 0
    expect(cell.center + cell.up + cell.down + cell.left + cell.right) == 3
    expect(cell.moves) == True


def test_plan_prefers_attacking_weaker_enemy():
    cells = [
        Cell(0, 0, Color.RED, 5, size=2),
        Cell(0, 1, Color.BLUE, 1, size=2),
        Cell(1, 0, Color.GREEN, 8, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    random.seed(1)
    autoplay.plan([cells[0]], player, board=cells)

    expect(cells[0].right) > cells[0].down
    expect(cells[0].right) >= 2


def test_plan_avoids_even_strength_attacks():
    cells = [
        Cell(0, 0, Color.RED, 3, size=2),
        Cell(0, 1, Color.BLUE, 3, size=2),
        Cell(1, 0, Color.NONE, 0, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    for seed in range(30):
        for cell in cells:
            cell.up = cell.down = cell.left = cell.right = 0
        cells[0].center = 3
        cells[0].color = Color.RED
        cells[1].center = 3
        cells[1].color = Color.BLUE
        cells[2].center = 0
        cells[2].color = Color.NONE
        cells[3].center = 0
        cells[3].color = Color.NONE

        random.seed(seed)
        autoplay.plan([cells[0]], player, board=cells)

        expect(cells[0].right) == 0


def test_plan_expands_into_empty_cells():
    cells = [
        Cell(0, 0, Color.RED, 4, size=2),
        Cell(0, 1, Color.NONE, 0, size=2),
        Cell(1, 0, Color.NONE, 0, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    random.seed(2)
    autoplay.plan([cells[0]], player, board=cells)

    expect(cells[0].right + cells[0].down) >= 2
    expect(cells[0].moves) == True


def test_plan_fortifies_threatened_ally():
    cells = [
        Cell(0, 0, Color.RED, 4, size=2),
        Cell(0, 1, Color.RED, 1, size=2),
        Cell(1, 0, Color.BLUE, 5, size=2),
        Cell(1, 1, Color.BLUE, 3, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    random.seed(3)
    autoplay.plan([cells[0]], player, board=cells)

    expect(cells[0].right) >= 1
    expect(cells[0].down) == 0


def test_plan_does_not_abandon_cell_to_stronger_ally():
    cells = [
        Cell(0, 0, Color.GREEN, 1, size=2),
        Cell(0, 1, Color.NONE, 0, size=2),
        Cell(1, 0, Color.GREEN, 6, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.GREEN, autoplay=True)

    for seed in range(30):
        for cell in cells:
            cell.up = cell.down = cell.left = cell.right = 0
        cells[0].center = 1
        cells[0].color = Color.GREEN
        cells[2].center = 6
        cells[2].color = Color.GREEN

        random.seed(seed)
        autoplay.plan([cells[0], cells[2]], player, board=cells)

        expect(
            cells[0].center
            + cells[0].up
            + cells[0].down
            + cells[0].left
            + cells[0].right
        ) >= 1
        expect(cells[0].down) == 0
        expect(cells[2].up) >= 1


def test_plan_keeps_garrison_when_threatened():
    cells = [
        Cell(0, 0, Color.RED, 3, size=2),
        Cell(0, 1, Color.BLUE, 2, size=2),
        Cell(1, 0, Color.NONE, 0, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    random.seed(4)
    autoplay.plan([cells[0]], player, board=cells)

    expect(cells[0].center) == 1


def test_plan_lone_unit_often_retreats_from_larger_enemy():
    cells = [
        Cell(0, 0, Color.RED, 1, size=2),
        Cell(0, 1, Color.BLUE, 4, size=2),
        Cell(1, 0, Color.RED, 2, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)
    retreated = 0

    for seed in range(40):
        for cell in cells:
            cell.up = cell.down = cell.left = cell.right = 0
        cells[0].center = 1
        cells[0].color = Color.RED
        cells[1].center = 4
        cells[1].color = Color.BLUE
        cells[2].center = 2
        cells[2].color = Color.RED
        cells[3].center = 0
        cells[3].color = Color.NONE

        random.seed(seed)
        autoplay.plan([cells[0]], player, board=cells)

        if cells[0].right == 0 and (cells[0].down or cells[0].center == 0):
            retreated += 1

    expect(retreated) >= 28


def test_plan_does_not_swap_units_between_friendly_cells():
    cells = [
        Cell(0, 0, Color.YELLOW, 3, size=2),
        Cell(0, 1, Color.YELLOW, 3, size=2),
        Cell(1, 0, Color.NONE, 0, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.YELLOW, autoplay=True)

    for seed in range(30):
        for cell in cells:
            cell.center = 3
            cell.up = cell.down = cell.left = cell.right = 0
        cells[2].color = Color.NONE
        cells[2].center = 0
        cells[3].color = Color.NONE
        cells[3].center = 0

        random.seed(seed)
        autoplay.plan([cells[0], cells[1]], player, board=cells)

        expect(min(cells[0].right, cells[1].left)) == 0


def test_cancel_opposing_transfers_returns_units_to_center():
    left = Cell(0, 0, Color.YELLOW, 0, right=2, size=2)
    right = Cell(0, 1, Color.YELLOW, 0, left=2, size=2)
    grid = autoplay._grid([left, right])

    cancelled = autoplay._cancel_opposing_transfers([left, right], grid)

    expect(cancelled) == 4
    expect(left.right) == 0
    expect(right.left) == 0
    expect(left.center) == 2
    expect(right.center) == 2


def test_delay_for_increases_around_the_circle(monkeypatch):
    monkeypatch.setattr(autoplay, "TESTING", False)

    expect(autoplay.delay_for(0)) == autoplay.DELAY
    expect(autoplay.delay_for(1)) == autoplay.DELAY * 2
    expect(autoplay.delay_for(2)) == autoplay.DELAY * 3


def test_delay_for_skips_wait_with_multiple_humans(monkeypatch):
    monkeypatch.setattr(autoplay, "TESTING", False)

    expect(autoplay.delay_for(0, humans=2)) == 0.0
    expect(autoplay.delay_for(2, humans=3)) == 0.0


def test_schedule_uses_seat_position(monkeypatch):
    monkeypatch.setattr(autoplay, "TESTING", False)
    now = 1000.0
    player = Player(Color.GREEN, autoplay=True)

    autoplay.schedule(player, position=1, humans=1, now=now)

    expect(player.state) == State.PLANNING
    expect(player.autoplay_until) == now + autoplay.DELAY * 2
