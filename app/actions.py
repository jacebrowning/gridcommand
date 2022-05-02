import random
from dataclasses import dataclass

import log

from .enums import Color
from .types import Cell


@dataclass
class Move:
    start: Cell
    direction: str
    finish: Cell

    def __str__(self):
        if self.direction == "left":
            return f"{self.finish.center} {self.finish} {self.arrow} {self.outgoing} {self.start}"
        return f"{self.outgoing} {self.start} {self.arrow} {self.finish.center} {self.finish}"

    def __bool__(self):
        raise NotImplementedError

    @property
    def outgoing(self) -> int:
        return getattr(self.start, self.direction)

    @property
    def incoming(self) -> int:
        return getattr(self.finish, self.reverse)

    @property
    def reverse(self):
        values = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }
        return values[self.direction]

    @property
    def arrow(self) -> str:
        values = {
            "up": "⇧",
            "down": "⇩",
            "left": "⇦",
            "right": "⇨",
            "left-right": "⬄",
            "up-down": "⇳",
        }
        return values[self.direction]

    def perform(self):
        raise NotImplementedError


@dataclass
class Fortification(Move):
    def __bool__(self):
        return bool(self.start.color == self.finish.color and self.outgoing)

    def perform(self):
        self.finish.center += self.outgoing
        setattr(self.start, self.direction, 0)
        if not self.start.center:
            self.start.color = Color.NONE


@dataclass
class BorderClash(Move):
    def __post_init__(self):
        if self.direction in {"up", "down"}:
            self.direction = "up-down"
        if self.direction in {"left", "right"}:
            self.direction = "left-right"

    def __str__(self):
        return (
            f"{self.outgoing} {self.start} {self.arrow} {self.incoming} {self.finish}"
        )

    def __bool__(self):
        return bool(
            self.start.color != self.finish.color and self.outgoing and self.incoming
        )

    @property
    def outgoing(self) -> int:
        return getattr(self.start, self.direction.split("-")[1])

    @property
    def incoming(self) -> int:
        return getattr(self.finish, self.direction.split("-")[0])

    def perform(self):
        while self.outgoing and self.incoming:
            offense = sorted(
                [random.randint(1, 6) for _ in range(self.outgoing)], reverse=True
            )
            defense = sorted(
                [random.randint(1, 6) for _ in range(self.incoming)], reverse=True
            )
            log.info(
                f"{self.outgoing} {self.start} @ {offense} vs. {self.incoming} {self.finish} @ {defense}"
            )
            if offense > defense:
                setattr(self.start, self.direction.split("-")[1], self.outgoing - 1)
            else:
                setattr(self.finish, self.direction.split("-")[0], self.incoming - 1)


@dataclass
class Attack(Move):
    def __bool__(self):
        return bool(
            self.start.color != self.finish.color
            and self.outgoing
            and not self.incoming
        )

    def perform(self):
        while self.outgoing and self.finish.center:
            offense = sorted(
                [random.randint(1, 6) for _ in range(self.outgoing)], reverse=True
            )
            defense = sorted(
                [random.randint(1, 6) for _ in range(self.finish.center)], reverse=True
            )
            log.info(
                f"{self.outgoing} {self.start} @ {offense} vs. {self.finish.center} {self.finish} @ {defense}"
            )
            if offense > defense:
                self.finish.center -= 1
            else:
                setattr(self.start, self.direction, self.outgoing - 1)

        if self.outgoing:
            self.finish.color = self.start.color
            self.finish.center = self.outgoing
            setattr(self.start, self.direction, 0)

        if not self.start.center:
            self.start.color = Color.NONE
