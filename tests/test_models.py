import random

import pytest
from expecter import expect

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


def test_living_excludes_players_with_no_cells(game):
    expect([p.color for p in game.living]) == [Color.BLUE]

    game.board.cells.append(Cell(1, 0, Color.RED, 1))
    expect([p.color for p in game.living]) == [Color.BLUE, Color.RED]


def test_show_results_eliminates_players_with_no_cells(game):
    game.round = 1
    for player in game.players:
        player.state = State.WAITING
        player.round = 1
    red = game.get_player("red")
    expect(red.autoplay) == True

    blue = game.get_player("blue")
    # Wipe blue's cells through combat-equivalent board state
    for cell in list(game.board.get_cells(Color.BLUE)):
        cell.color = Color.NONE
        cell.center = 0

    game.show_results()

    expect(blue.autoplay) == True
    expect(blue.state) == State.WAITING
    expect(blue in game.living) == False


def test_humans_done_planning_skips_dead_humans(game):
    game.round = 1
    blue = game.get_player("blue")
    blue.autoplay = False
    blue.state = State.PLANNING
    blue.round = 1
    for cell in list(game.board.get_cells(Color.BLUE)):
        cell.color = Color.NONE
        cell.center = 0

    expect(game._humans_done_planning()) == True


def test_fortify(game):
    game.advance()
    expect(game.board.cells) == [
        Cell(0, 0, Color.BLUE, 2),
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


def test_reinforcement_count_scales_with_territories(game):
    expect(game.board.reinforcement_count(game.players[0])) == 3  # 6 blue cells

    game.board.cells = [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 1),
        Cell(0, 2, Color.BLUE, 1),
        Cell(0, 3, Color.BLUE, 1),
    ]
    expect(game.board.reinforcement_count(game.players[0])) == 2

    game.board.cells = [
        Cell(0, 0, Color.BLUE, 1),
        Cell(0, 1, Color.BLUE, 1),
        Cell(0, 2, Color.BLUE, 1),
        Cell(0, 3, Color.BLUE, 1),
        Cell(0, 4, Color.BLUE, 1),
    ]
    expect(game.board.reinforcement_count(game.players[0])) == 2

    game.board.cells = [Cell(0, 0, Color.BLUE, 1)]
    expect(game.board.reinforcement_count(game.players[0])) == 1

    game.board.cells = []
    expect(game.board.reinforcement_count(game.players[0])) == 0


def test_initialize_gives_all_players_equal_units():
    game = Game()
    game.initialize(players=2)

    expect(len(game.humans)) == 2
    for player in game.players:
        owned = list(game.board.get_cells(player.color))
        expect(len(owned)) >= 1
        expect(sum(cell.value for cell in owned)) == game.board.size * 3


def test_initialize_fill_gives_each_player_at_least_two_cells():
    game = Game()
    game.fill = True
    for seed in range(20):
        random.seed(seed)
        game.initialize(size=3, players=4)
        for player in game.players:
            owned = list(game.board.get_cells(player.color))
            expect(len(owned)) >= 2
            expect(sum(cell.value for cell in owned)) == 9


def test_initialize_corners_only_when_fill_disabled():
    game = Game()
    game.fill = False
    game.initialize(size=4, players=2)

    owned = [cell for cell in game.board.cells if cell.color is not Color.NONE]
    expect(len(owned)) == 4
    for player in game.players:
        cells = list(game.board.get_cells(player.color))
        expect(len(cells)) == 1
        expect(cells[0].value) == 12


def test_initialize_starting_units_scale_with_board_size():
    game = Game()
    game.fill = False
    game.initialize(size=3, players=2)
    for player in game.players:
        expect(sum(cell.value for cell in game.board.get_cells(player.color))) == 9

    game.initialize(size=5, players=2)
    for player in game.players:
        expect(sum(cell.value for cell in game.board.get_cells(player.color))) == 15


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


def test_tick_advances_phases_when_only_computers_remain(game):
    game.round = 1
    game.phase = "results"
    for player in game.players:
        player.autoplay = True
        player.state = State.WAITING
        player.round = 1
    game.board.cells.append(Cell(1, 0, Color.RED, 2))

    game.tick()
    expect(game.phase) == "reinforcements"

    game.tick()
    expect(game.phase) == ""
    expect(game.round) == 2
