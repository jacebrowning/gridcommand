import random
import time
from typing import Optional

import log

from .constants import TESTING
from .enums import State
from .types import Cell, Player

DELAY = 2.0  # seconds between each computer around the circle


def plan(cells: list[Cell], player: Player) -> int:
    """Randomly commit units to adjacent cells for an autoplay player."""
    count = 0
    for cell in cells:
        directions = [
            direction
            for direction, able in (
                ("up", cell.can_move_up),
                ("down", cell.can_move_down),
                ("left", cell.can_move_left),
                ("right", cell.can_move_right),
            )
            if able
        ]
        if not directions or not cell.center:
            continue
        moving = random.randint(0, cell.center)
        for _ in range(moving):
            direction = random.choice(directions)
            cell.center -= 1
            setattr(cell, direction, getattr(cell, direction) + 1)
            count += 1
    if count:
        s = "" if count == 1 else "s"
        log.info(f"Planned {count} move{s} for {player}")
    return count


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
