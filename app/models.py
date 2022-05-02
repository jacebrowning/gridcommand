import random
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterator

import datafiles
from flask import url_for

from .actions import Attack, BorderClash, Fortification
from .constants import FILL, SIZE, UNITS, generate_code
from .enums import Color, State
from .types import Cell, Player


@dataclass
class Board:

    cells: list[Cell] = field(default_factory=list)

    def __iter__(self) -> Iterator[list[Cell]]:
        index = 0
        row = []
        for cell in self.cells:
            if cell.row == index:
                row.append(cell)
            else:
                yield row
                row = [cell]
                index += 1
        yield row

    def __getitem__(self, xy: tuple[int, int]) -> Cell:
        row, col = xy
        for cell in self.cells:
            if cell.row == row and cell.col == col:
                return cell
        raise LookupError(f"Unknown cell: {xy}")

    @property
    def fortifications(self) -> Iterator[Fortification]:
        for start in self.cells:
            for direction, finish in self.get_neighbors(start):
                if move := Fortification(start, direction, finish):
                    yield move

    @property
    def border_clashes(self) -> Iterator[BorderClash]:
        pairs = set()
        for start in self.cells:
            for direction, finish in self.get_neighbors(start):
                pair = tuple(sorted([start, finish]))  # type: ignore
                if pair not in pairs:
                    pairs.add(pair)
                    if move := BorderClash(start, direction, finish):
                        yield move

    @property
    def attacks(self) -> Iterator[Attack]:
        for start in self.cells:
            for direction, finish in self.get_neighbors(start):
                if move := Attack(start, direction, finish):
                    yield move

    def get_neighbors(self, cell: Cell) -> Iterator[tuple[str, Cell]]:
        with suppress(LookupError):
            xy = cell.row, cell.col - 1
            yield "left", self[xy]
        with suppress(LookupError):
            xy = cell.row, cell.col + 1
            yield "right", self[xy]
        with suppress(LookupError):
            xy = cell.row - 1, cell.col
            yield "up", self[xy]
        with suppress(LookupError):
            xy = cell.row + 1, cell.col
            yield "down", self[xy]

    def reset(self):
        assert SIZE <= 5  # see board.html width limits
        self.cells = []
        for row in range(SIZE):
            for col in range(SIZE):
                self.cells.append(Cell(row, col))


@datafiles.datafile("../data/games/{self.code}.yml", defaults=True)
class Game:

    code: str = field(default_factory=generate_code)

    round: int = 0
    players: list[Player] = field(
        # TODO: Support more than two players
        default_factory=lambda: [Player(Color.BLUE), Player(Color.RED)]
    )
    board: Board = Board()

    @cached_property
    def url(self) -> str:
        return url_for("setup", code=self.code, _external=True)

    @cached_property
    def choosing(self) -> int:
        return sum(1 for p in self.players if p.state is State.UNKNOWN)

    @cached_property
    def waiting(self) -> int:
        if any(p.round < self.round for p in self.players):
            return 0
        return sum(1 for p in self.players if p.state is not State.WAITING)

    @property
    def message(self) -> str:
        if self.round == 0:
            return ""
        if self.choosing:
            s = "" if self.choosing == 1 else "s"
            return f"Waiting for {self.choosing} player{s} to pick a color..."
        if self.waiting:
            s = "" if self.waiting == 1 else "s"
            return f"Waiting for {self.waiting} player{s} to plan moves..."
        return ""

    def initialize(self):
        units = {player.color: UNITS for player in self.players}
        cells = {player.color: [] for player in self.players}
        with datafiles.frozen(self):
            self.board.reset()
            for cell in self.board.cells:
                if random.random() < FILL:
                    player = random.choice(self.players)
                    cell.color = player.color
                    cell.center = 1
                    units[player.color] -= 1
                    cells[player.color].append(cell)
            for color, count in units.items():
                for _ in range(count):
                    cell = random.choice(cells[color])
                    cell.center += 1

    def get_player(self, color: str) -> Player:
        _color = Color[color.upper()]
        for player in self.players:
            if player.color is _color:
                return player
        raise ValueError(f"Unknown player color: {color}")
