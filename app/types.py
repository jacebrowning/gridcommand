from dataclasses import dataclass

import datafiles

from .constants import SIZE
from .enums import Color, State


@dataclass
class Player:
    color: Color
    round: int = 0
    state: State = State.UNKNOWN


@dataclass(order=True)
class Cell:
    row: int
    col: int

    color: Color = Color.NONE

    center: int = 0
    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0

    def __str__(self):
        return f"{self.color.icon} ({self.row},{self.col})"

    def __bool__(self):
        return self.color is not Color.NONE

    def __hash__(self):
        return hash((self.row, self.col))

    @property
    def value(self) -> int:
        return self.center + self.up + self.down + self.left + self.right

    @property
    def can_move_up(self) -> bool:
        return self.row > 0

    @property
    def can_move_down(self) -> bool:
        return self.row < SIZE - 1

    @property
    def can_move_left(self) -> bool:
        return self.col > 0

    @property
    def can_move_right(self) -> bool:
        return self.col < SIZE - 1

    @property
    def moves(self) -> bool:
        return any((self.up, self.down, self.left, self.right))

    # TODO: Move this logic

    def move(self, count: int, direction: str):
        if self.center:
            with datafiles.frozen(self):
                self.center -= count
                value = getattr(self, direction)
                setattr(self, direction, value + count)

    def reset(self):
        with datafiles.frozen(self):
            self.center = self.center + self.up + self.down + self.left + self.right
            self.up = self.down = self.left = self.right = 0
