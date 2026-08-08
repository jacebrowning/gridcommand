import pytest
from expecter import expect

from app.constants import UNITS
from app.enums import Color, State
from app.models import Cell, Game


@pytest.fixture
def game():
    g = Game()
    g.initialize(players=1)
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


def test_humans(game):
    expect(len(game.players)) == 4
    expect(len(game.humans)) == 1


def test_fortify(game):
    game.advance()
    expect(game.board.cells) == [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 3),
        Cell(0, 2, Color.NONE, 0),
        Cell(0, 3, Color.BLUE, 4),
        Cell(0, 4, Color.BLUE, 1),
        Cell(0, 5, Color.BLUE, 1),
        Cell(0, 6, Color.BLUE, 1),
    ]


def test_show_reinforcements_previews_counts(game):
    game.board.cells.append(Cell(1, 0, Color.RED, 1))
    game.round = 1
    for player in game.players:
        player.state = State.WAITING
        player.round = 1
    game.phase = "results"

    game.show_reinforcements()

    expect(game.phase) == "reinforcements"
    expect(game.board.cells[1].center) == 2
    expect(game.board.cells[1].extra) == 1
    expect(game.board.cells[3].center) == 3
    expect(game.board.cells[3].extra) == 1


def test_initialize_gives_all_players_equal_units():
    game = Game()
    game.initialize(players=2)

    expect(len(game.humans)) == 2
    for player in game.players:
        owned = list(game.board.get_cells(player.color))
        expect(len(owned)) >= 1
        expect(sum(cell.value for cell in owned)) == UNITS


def test_initialize_corners_only_when_fill_disabled():
    game = Game()
    game.fill = False
    game.initialize(size=4, players=2)

    owned = [cell for cell in game.board.cells if cell.color is not Color.NONE]
    expect(len(owned)) == 4
    for player in game.players:
        cells = list(game.board.get_cells(player.color))
        expect(len(cells)) == 1
        expect(cells[0].value) == UNITS


def test_planning_includes_computer_players():
    game = Game()
    game.initialize(players=1)
    game.round = 1
    for player in game.humans:
        player.state = State.PLANNING
        player.round = game.round

    expect(game.planning) == 4


def test_tick_autoplay_waits_until_humans_finish_planning():
    game = Game()
    game.initialize(players=1)
    game.round = 1
    for player in game.humans:
        player.state = State.PLANNING
        player.round = game.round

    game.tick_autoplay()

    expect(any(player.autoplay_until for player in game.players)) == False
    expect(game.planning) == 4


def test_tick_autoplay_finishes_computers_after_delay():
    game = Game()
    game.initialize(players=1)
    game.round = 1
    for player in game.humans:
        player.state = State.WAITING
        player.round = game.round

    expect(game.planning) == 3

    game.tick_autoplay()

    expect(game.planning) == 0
    autoplay_cells = [
        cell
        for player in game.players
        if player.autoplay
        for cell in game.board.get_cells(player.color)
    ]
    expect(any(cell.moves for cell in autoplay_cells)) == True

    before = [
        (cell.center, cell.up, cell.down, cell.left, cell.right)
        for cell in autoplay_cells
    ]
    game.tick_autoplay()
    after = [
        (cell.center, cell.up, cell.down, cell.left, cell.right)
        for cell in autoplay_cells
    ]
    expect(after) == before
