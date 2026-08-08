import random

from expecter import expect

from app import autoplay
from app.enums import Color, State
from app.types import Cell, Player


def test_plan_moves_units_randomly():
    cells = [
        Cell(0, 0, Color.RED, 3, size=2),
        Cell(0, 1, Color.NONE, 0, size=2),
        Cell(1, 0, Color.NONE, 0, size=2),
        Cell(1, 1, Color.NONE, 0, size=2),
    ]
    player = Player(Color.RED, autoplay=True)

    random.seed(0)
    moved = autoplay.plan([cells[0]], player)

    cell = cells[0]
    expect(moved) > 0
    expect(cell.center + cell.up + cell.down + cell.left + cell.right) == 3
    expect(cell.moves) == True


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
