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

# Attack with at least this many more units than the defender.
ATTACK_MARGIN = 1


def plan(
    cells: list[Cell],
    player: Player,
    *,
    board: Optional[list[Cell]] = None,
) -> int:
    """Commit units for an autoplay player (mass attacks, then local plans)."""
    grid = _grid(board if board is not None else cells)
    count = 0
    if board is not None:
        count += _commit_mass_attacks(cells, player.color, grid)
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


def _direction_toward(start: Cell, finish: Cell) -> Optional[str]:
    dr = finish.row - start.row
    dc = finish.col - start.col
    for direction, (adr, adc) in DELTA.items():
        if (dr, dc) == (adr, adc):
            return direction
    return None


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


def _surplus(cell: Cell) -> int:
    """Units that can move while keeping a garrison when possible."""
    if cell.center <= 1:
        return 0
    return cell.center - 1


def _send(cell: Cell, direction: str, amount: int) -> int:
    sent = 0
    for _ in range(amount):
        if cell.center <= 0:
            break
        cell.center -= 1
        setattr(cell, direction, getattr(cell, direction) + 1)
        sent += 1
    return sent


def _commit_mass_attacks(
    cells: list[Cell], color: Color, grid: dict[tuple[int, int], Cell]
) -> int:
    """Coordinate 2+ stacks into one enemy when combined force is superior."""
    owned = {(cell.row, cell.col) for cell in cells}
    enemies = [
        cell
        for cell in grid.values()
        if cell.color not in {Color.NONE, color} and cell.value > 0
    ]

    targets: list[tuple[tuple[int, int, int], Cell, list[tuple[Cell, str, int]]]] = []
    for enemy in enemies:
        supporters: list[tuple[Cell, str, int]] = []
        for direction in DELTA:
            neighbor = _neighbor(grid, enemy, direction)
            if neighbor is None or (neighbor.row, neighbor.col) not in owned:
                continue
            toward = _direction_toward(neighbor, enemy)
            if toward is None:
                continue
            available = _surplus(neighbor)
            if available:
                supporters.append((neighbor, toward, available))
        if len(supporters) < 2:
            continue
        total = sum(available for _, _, available in supporters)
        need = enemy.value + ATTACK_MARGIN
        if total < need:
            continue
        # Prefer weaker enemies with more overlapping force.
        priority = (enemy.value, -total, -len(supporters))
        targets.append((priority, enemy, supporters))

    targets.sort(key=lambda item: item[0])
    moved = 0
    for _, enemy, supporters in targets:
        need = enemy.value + ATTACK_MARGIN
        live = []
        for cell, direction, _ in supporters:
            available = _surplus(cell)
            if available:
                live.append((cell, direction, available))
        if len(live) < 2:
            continue
        total = sum(available for _, _, available in live)
        if total < need:
            continue

        remaining = need
        # Ensure at least two directions participate (mass attack).
        for cell, direction, _ in live[:2]:
            if remaining <= 0:
                break
            if cell.center <= 1:
                continue
            sent = _send(cell, direction, 1)
            remaining -= sent
            moved += sent

        while remaining > 0:
            progress = False
            for cell, direction, _ in live:
                if remaining <= 0:
                    break
                if cell.center <= 1:
                    continue
                sent = _send(cell, direction, 1)
                if sent:
                    remaining -= sent
                    moved += sent
                    progress = True
            if not progress:
                break
    return moved


def _score(
    cell: Cell,
    direction: str,
    neighbor: Cell,
    color: Color,
    grid: dict[tuple[int, int], Cell],
    *,
    retreat: bool = False,
    territories: int = 1,
) -> float:
    committed = getattr(cell, direction)

    if neighbor.color is Color.NONE:
        # Claim empty ground; economy spike at 4 cells makes early expands critical.
        if committed >= 3:
            score = 1.0
        else:
            score = 12.0 - committed * 3.0
        if territories < 4:
            score += 8.0
        return score + 10.0 if retreat else score

    if neighbor.color is color:
        if getattr(neighbor, REVERSE[direction]):
            return 0.0
        if not retreat and neighbor.value >= cell.value:
            return 0.0
        threats = _enemy_adjacent(grid, neighbor, color)
        weakness = max(0, 4 - neighbor.value)
        score = 4.0 + threats * 4.0 + weakness * 2.0 - committed * 0.5
        return score + 14.0 if retreat else score

    defense = neighbor.value
    if retreat and defense > cell.center:
        return 0.0
    next_force = committed + 1
    max_force = committed + cell.center
    if max_force <= defense:
        return 0.0
    # Only finish attacks that keep numerical superiority.
    if next_force <= defense:
        return 10.0 + (max_force - defense)
    if next_force < defense + ATTACK_MARGIN:
        return 0.0
    if next_force > defense + 2:
        return 0.5
    # Prefer hitting weaker enemies (income denial + easier wins).
    return 16.0 + (next_force - defense) + max(0, 5 - defense)


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


def _pick_direction(options: list[tuple[str, Cell]], weights: list[float]) -> str:
    best = max(weights)
    tied = [
        direction for (direction, _), weight in zip(options, weights) if weight == best
    ]
    return random.choice(tied)


def _plan_cell(cell: Cell, color: Color, grid: dict[tuple[int, int], Cell]) -> int:
    if not cell.center:
        return 0

    options: list[tuple[str, Cell]] = []
    for direction in _reachable(cell):
        neighbor = _neighbor(grid, cell, direction)
        if neighbor is not None:
            options.append((direction, neighbor))

    if not options:
        directions = _reachable(cell)
        if not directions:
            return 0
        moving = random.randint(0, cell.center)
        for _ in range(moving):
            direction = random.choice(directions)
            cell.center -= 1
            setattr(cell, direction, getattr(cell, direction) + 1)
        return moving

    territories = sum(1 for c in grid.values() if c.color is color)
    retreat = (
        cell.center == 1
        and _threatened_by_larger(grid, cell, color)
        and random.random() < 0.8
    )
    keep = 0 if retreat else 1
    moved = 0

    while cell.center > keep:
        weights = [
            max(
                _score(
                    cell,
                    direction,
                    neighbor,
                    color,
                    grid,
                    retreat=retreat,
                    territories=territories,
                ),
                0.0,
            )
            for direction, neighbor in options
        ]
        if not any(weights):
            break
        direction = _pick_direction(options, weights)
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
