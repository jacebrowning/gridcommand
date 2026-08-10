import random
import time
from typing import Optional

import log

from .constants import TESTING
from .enums import Color, State
from .types import Cell, Player

DELAY = 2.0  # seconds between each computer around the circle

DIRECTIONS = (
    ("up", "can_move_up"),
    ("down", "can_move_down"),
    ("left", "can_move_left"),
    ("right", "can_move_right"),
)

DELTA = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

REVERSE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}


def plan(
    cells: list[Cell],
    player: Player,
    *,
    board: Optional[list[Cell]] = None,
) -> int:
    """Commit units toward useful adjacent cells for an autoplay player."""
    grid = _grid(board if board is not None else cells)
    count = 0
    for cell in cells:
        count += _plan_cell(cell, player.color, grid)
    count -= _cancel_opposing_transfers(cells, grid)
    if count:
        s = "" if count == 1 else "s"
        log.info(f"Planned {count} move{s} for {player}")
    return count


def _grid(cells: list[Cell]) -> dict[tuple[int, int], Cell]:
    return {(cell.row, cell.col): cell for cell in cells}


def _neighbor(
    grid: dict[tuple[int, int], Cell], cell: Cell, direction: str
) -> Optional[Cell]:
    dr, dc = DELTA[direction]
    return grid.get((cell.row + dr, cell.col + dc))


def _reachable(cell: Cell) -> list[str]:
    return [direction for direction, able in DIRECTIONS if getattr(cell, able)]


def _enemy_adjacent(grid: dict[tuple[int, int], Cell], cell: Cell, color: Color) -> int:
    count = 0
    for direction in DELTA:
        neighbor = _neighbor(grid, cell, direction)
        if neighbor and neighbor.color not in {Color.NONE, color}:
            count += 1
    return count


def _threatened_by_larger(
    grid: dict[tuple[int, int], Cell], cell: Cell, color: Color
) -> bool:
    for direction in DELTA:
        neighbor = _neighbor(grid, cell, direction)
        if (
            neighbor
            and neighbor.color not in {Color.NONE, color}
            and neighbor.value > cell.center
        ):
            return True
    return False


def _score(
    cell: Cell,
    direction: str,
    neighbor: Cell,
    color: Color,
    grid: dict[tuple[int, int], Cell],
    *,
    retreat: bool = False,
) -> float:
    committed = getattr(cell, direction)

    if neighbor.color is Color.NONE:
        # Claim empty ground; a couple units are usually enough.
        if committed >= 3:
            score = 1.0
        else:
            score = 12.0 - committed * 3.0
        return score + 10.0 if retreat else score

    if neighbor.color is color:
        # Never swap units with a friendly cell that is already sending back.
        if getattr(neighbor, REVERSE[direction]):
            return 0.0
        # Don't drain into equal/stronger allies — reinforce weaker cells instead.
        if not retreat and neighbor.value >= cell.value:
            return 0.0
        threats = _enemy_adjacent(grid, neighbor, color)
        weakness = max(0, 4 - neighbor.value)
        score = 4.0 + threats * 4.0 + weakness * 2.0 - committed * 0.5
        # Lone units prefer consolidating into allies over standing ground.
        return score + 14.0 if retreat else score

    # Enemy: only attack with numerical superiority; even fights are too risky.
    defense = neighbor.value
    if retreat and defense > cell.center:
        return 0.0
    next_force = committed + 1
    max_force = committed + cell.center
    if max_force <= defense:
        return 0.0
    if next_force <= defense:
        return 10.0 + (max_force - defense)
    if next_force > defense + 2:
        return 0.5
    return 16.0 + (next_force - defense)


def _cancel_opposing_transfers(
    cells: list[Cell], grid: dict[tuple[int, int], Cell]
) -> int:
    """Return wasted friendly head-to-head moves back to center."""
    cancelled = 0
    for cell in cells:
        for direction in ("right", "down"):
            neighbor = _neighbor(grid, cell, direction)
            if neighbor is None or neighbor.color is not cell.color:
                continue
            reverse = REVERSE[direction]
            outgoing = getattr(cell, direction)
            incoming = getattr(neighbor, reverse)
            overlap = min(outgoing, incoming)
            if not overlap:
                continue
            setattr(cell, direction, outgoing - overlap)
            setattr(neighbor, reverse, incoming - overlap)
            cell.center += overlap
            neighbor.center += overlap
            cancelled += overlap * 2
    return cancelled


def _plan_cell(cell: Cell, color: Color, grid: dict[tuple[int, int], Cell]) -> int:
    if not cell.center:
        return 0

    options: list[tuple[str, Cell]] = []
    for direction in _reachable(cell):
        neighbor = _neighbor(grid, cell, direction)
        if neighbor is not None:
            options.append((direction, neighbor))

    if not options:
        # No board context: fall back to edge-aware random moves.
        directions = _reachable(cell)
        if not directions:
            return 0
        moving = random.randint(0, cell.center)
        for _ in range(moving):
            direction = random.choice(directions)
            cell.center -= 1
            setattr(cell, direction, getattr(cell, direction) + 1)
        return moving

    retreat = (
        cell.center == 1
        and _threatened_by_larger(grid, cell, color)
        and random.random() < 0.8
    )
    # Hold territory unless deliberately retreating from a larger enemy.
    keep = 0 if retreat else 1
    moved = 0

    while cell.center > keep:
        weights = [
            max(
                _score(cell, direction, neighbor, color, grid, retreat=retreat),
                0.0,
            )
            for direction, neighbor in options
        ]
        if not any(weights):
            break
        direction = random.choices(
            [direction for direction, _ in options], weights=weights, k=1
        )[0]
        cell.center -= 1
        setattr(cell, direction, getattr(cell, direction) + 1)
        moved += 1

    return moved


def delay_for(position: int, *, humans: int = 1) -> float:
    """Return how long the computer at this seat should wait before finishing."""
    if TESTING or humans >= 2:
        return 0.0
    return DELAY * (position + 1)


def schedule(
    player: Player,
    *,
    position: int = 0,
    humans: int = 1,
    now: Optional[float] = None,
) -> None:
    """Put a computer player into planning with a seat-ordered completion time."""
    now = time.time() if now is None else now
    player.state = State.PLANNING
    player.autoplay_until = now + delay_for(position, humans=humans)


def due(player: Player, now: Optional[float] = None) -> bool:
    now = time.time() if now is None else now
    return bool(player.autoplay_until) and now >= player.autoplay_until
