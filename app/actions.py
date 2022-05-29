import random
from dataclasses import dataclass
from typing import Protocol

import log

from .constants import TESTING
from .enums import Color
from .types import Cell


def roll(count: int) -> list[int]:
    return sorted([random.randint(1, 6) for _ in range(count)], reverse=True)


class Performable(Protocol):
    def __bool__(self):
        raise NotImplementedError

    @property
    def outgoing(self) -> int:
        """Number of units moving from the attack to the defense."""
        raise NotImplementedError

    @property
    def incoming(self) -> int:
        """Number of units moving from the defense to the attack."""
        raise NotImplementedError

    def perform(self):
        """Execute the move until one side is eliminated."""
        raise NotImplementedError


@dataclass
class Move(Performable):
    start: Cell
    direction: str
    finish: Cell

    def __str__(self):
        if self.direction == "left":
            return f"{self.finish.center}ˣ{self.finish} {self.arrow} {self.outgoing}ˣ{self.start}"
        return f"{self.outgoing}ˣ{self.start} {self.arrow} {self.finish.center}ˣ{self.finish}"

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
        log.info(f"Performing fortification: {self}")
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
        log.info(f"Performing border clash: {self}")
        one = self.start.color.title
        two = self.finish.color.title
        while self.outgoing and self.incoming:
            attack = roll(self.outgoing)
            defense = roll(self.incoming)
            log.info(f"{one} rolled: {attack}")
            log.info(f"{two} rolled: {defense}")
            while attack and defense:
                if attack[0] > defense[0]:
                    log.info(f"{one} won roll: {attack} > {defense}")
                    setattr(
                        self.finish, self.direction.split("-")[0], self.incoming - 1
                    )
                elif defense[0] > attack[0]:
                    log.info(f"{two} won roll: {attack} < {defense}")
                    setattr(self.start, self.direction.split("-")[1], self.outgoing - 1)
                else:
                    log.info(f"Stalemate roll: {attack} = {defense}")
                attack.pop(0)
                defense.pop(0)

        if self.outgoing:
            log.info(f"{one} won border clash: {self.outgoing} persisted")
        else:
            log.info(f"{two} won border clash: {self.incoming} persisted")


@dataclass
class Attack(Move):
    def __bool__(self):
        return bool(
            self.start.color != self.finish.color
            and self.outgoing
            and not self.incoming
        )

    def __lt__(self, other):
        return self.outgoing < other.outgoing

    def perform(self):
        action = "attack" if self.finish.center else "march"
        log.info(f"Performing {action}: {self}")
        while self.outgoing and self.finish.center:
            attack = roll(self.outgoing)
            defense = roll(self.finish.center)
            log.info(f"Attack rolled: {attack}")
            log.info(f"Defense rolled: {defense}")
            while attack and defense:
                if attack[0] > defense[0]:
                    log.info(f"Attack won roll: {attack} > {defense}")
                    self.finish.center -= 1
                else:
                    log.info(f"Defense won roll: {attack} < {defense}")
                    setattr(self.start, self.direction, self.outgoing - 1)
                attack.pop(0)
                defense.pop(0)

        if self.outgoing:
            if action != "march":
                log.info(f"Attack won attack: {self.outgoing} persisted")
            if TESTING:
                assert not self.finish.moves
            self.finish.color = self.start.color
            self.finish.center = self.outgoing
            setattr(self.start, self.direction, 0)
        else:
            log.info(f"Defense won attack: {self.finish.center} persisted")

        if not self.start.center:
            self.start.color = Color.NONE


@dataclass
class AttackWithRetreat(Attack):
    def __bool__(self):
        return super().__bool__() and not self.finish.moves


@dataclass
class MassAttack(Performable):
    moves: list[Attack]
    finish: Cell

    def __bool__(self):
        if not self.finish.value:
            return False
        count = sum(1 for move in self.moves if move)
        return count >= 2

    def __str__(self):
        return " ➕ ".join(str(m) for m in self.moves)

    @property
    def outgoing(self) -> int:
        count = 0
        for move in self.moves:
            count += move.outgoing
        return count

    def perform(self):
        log.info(f"Performing mass attack: {self}")
        while self.outgoing and self.finish.center:
            attack = roll(self.outgoing)
            defense = roll(self.finish.center)
            log.info(f"Attack rolled: {attack}")
            log.info(f"Defense rolled: {defense}")
            while attack and defense:
                if attack[0] > defense[0]:
                    log.info(f"Attack won roll: {attack} > {defense}")
                    self.finish.center -= 1
                else:
                    log.info(f"Defense won roll: {attack} < {defense}")
                    moves = [m for m in sorted(self.moves) if m.outgoing]
                    move = moves[0]
                    setattr(move.start, move.direction, move.outgoing - 1)
                attack.pop(0)
                defense.pop(0)

        if self.outgoing:
            log.info(f"Attack won mass attack: {self.outgoing} persisted")
            if not self.finish.value:
                self.finish.color = Color.NONE
        else:
            log.info(f"Defense won mass attack: {self.finish.center} persisted")

        for move in self.moves:
            if not move.start.value:
                move.start.color = Color.NONE

        log.c(f"{self.finish=} / {self.finish.down=}")
