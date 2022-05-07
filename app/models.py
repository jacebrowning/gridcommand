import random
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain
from typing import Iterator

import datafiles
import log
from flask import url_for

from .actions import Attack, BorderClash, Fortification
from .constants import FILL, PLAYERS, SIZE, UNITS, generate_code
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
                else:
                    log.debug(f"Skipped non-fortification: {move}")

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
                    else:
                        log.debug(f"Skipped non-clash: {move}")

    @property
    def attacks(self) -> Iterator[Attack]:
        for start in self.cells:
            for direction, finish in self.get_neighbors(start):
                if move := Attack(start, direction, finish):
                    yield move
                else:
                    log.debug(f"Skipped non-attack: {move}")

    def get_cells(self, color: Color) -> Iterator[Cell]:
        for cell in self.cells:
            if cell.color is color:
                yield cell

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

    def advance(self) -> int:
        count = 0
        for move in chain(
            self.fortifications,
            self.border_clashes,
            # TODO: Handle mass attacks
            # TODO: Handle spoils of war
            self.attacks,
            self.fortifications,  # handle mass fortifications
        ):
            move.perform()
            count += 1

        s = "" if count == 1 else "s"
        log.info(f"Applied {count} move{s}")
        return count


@datafiles.datafile("../data/games/{self.code}.yml", defaults=True)
class Game:

    code: str = field(default_factory=generate_code)

    round: int = 0
    players: list[Player] = field(default_factory=Player.defaults)
    board: Board = Board()

    @cached_property
    def url(self) -> str:
        return url_for("setup", code=self.code, _external=True)

    @cached_property
    def choosing(self) -> int:
        return sum(1 for p in self.players if p.state is State.UNKNOWN)

    @cached_property
    def planning(self) -> int:
        count = 0
        for player in self.players:
            if player.autoplay:
                pass
            elif player.state is not State.WAITING:
                log.info(f"Waiting for {player} to plan their moves")
                count += 1
            elif player.round < self.round:
                log.info(f"Waiting for {player} to advance the game")
                count += 1
        return count

    @property
    def message(self) -> str:
        if self.round == 0:
            return ""
        if self.choosing:
            s = "" if self.choosing == 1 else "s"
            return f"Waiting for {self.choosing} player{s} to pick a color..."
        if self.planning:
            s = "" if self.planning == 1 else "s"
            return f"Waiting for {self.planning} player{s} to plan moves..."
        return ""

    def initialize(self):
        if PLAYERS == 1:
            self.players = self.players[:2]
            self.players[-1].autoplay = True
        else:
            self.players = self.players[:PLAYERS]
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

    def advance(self) -> int:
        count = self.board.advance()
        self.round += 1
        for player in self.players:
            if not any(self.board.get_cells(player.color)):
                log.info(f"Player eliminated: {player}")
                player.autoplay = True
        return count

    def get_player(self, color: str) -> Player:
        _color = Color[color.upper()]
        for player in self.players:
            if player.color is _color:
                return player
        raise ValueError(f"Unknown player color: {color}")
