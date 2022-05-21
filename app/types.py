from dataclasses import dataclass

import log

from .constants import SIZE, TESTING
from .enums import Color, State


@dataclass
class Player:
    color: Color
    round: int = 0
    state: State = State.UNKNOWN
    autoplay: bool = False

    @classmethod
    def defaults(cls) -> list["Player"]:
        return [
            cls(Color.BLUE),
            cls(Color.RED),
            cls(Color.GREEN),
            cls(Color.YELLOW),
        ]

    def __post_init__(self):
        if self.autoplay and self.state is State.UNKNOWN:
            self.state = State.WAITING

    def __str__(self):
        return self.color.key


@dataclass(order=True)
class Cell:
    row: int
    col: int

    color: Color = Color.NONE
    center: int = 0

    # TODO: Enable this once PythonAnywhere supports Python 3.10
    # _: KW_ONLY

    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0

    size: int = SIZE

    def __post_init__(self):
        if self.color is Color.NONE:
            message = f"Unowned cell {self.point} contains {self.value} unit(s)"
            if self.value:
                log.error(message)
                if TESTING:
                    raise ValueError(message)
                else:
                    self.center = 0
        else:
            message = f"Empty cell owned by {self.color.key} player"
            if not self.value:
                log.error(message)
                if TESTING:
                    raise ValueError(message)
                else:
                    self.color = Color.NONE

    def __repr__(self):
        return f"<cell: {self.value}ˣ{self}>"

    def __str__(self):
        return f"{self.color.icon} ﹫{self.point}"

    def __bool__(self):
        return self.color is not Color.NONE

    def __hash__(self):
        return hash((self.row, self.col))

    @property
    def point(self) -> str:
        return f"({self.row},{self.col})"

    @property
    def value(self) -> int:
        return self.center + self.up + self.down + self.left + self.right

    @property
    def can_move_up(self) -> bool:
        return self.row > 0

    @property
    def can_move_down(self) -> bool:
        return self.row < self.size - 1

    @property
    def can_move_left(self) -> bool:
        return self.col > 0

    @property
    def can_move_right(self) -> bool:
        return self.col < self.size - 1

    @property
    def moves(self) -> bool:
        return any((self.up, self.down, self.left, self.right))
