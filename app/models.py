import math
import random
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain
from typing import Iterator

import datafiles
import log
from flask import url_for

from .actions import Attack, BorderClash, Fortification, MassAttack
from .constants import EXTRA, FILL, PLAYERS, SIZE, UNITS, generate_code
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
    def size(self) -> int:
        return int(math.sqrt(len(self.cells)))

    @property
    def tactical_moves(self) -> Iterator[Fortification]:
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
    def mass_attacks(self) -> Iterator[MassAttack]:
        for finish in self.cells:
            moves = []
            for direction, start in self.get_neighbors(finish, invert=True):
                if attack := Attack(start, direction, finish):
                    moves.append(attack)
            if moves:
                if move := MassAttack(moves, finish):
                    yield move
                else:
                    log.debug(f"Skipped not-mass: {move}")

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

    def get_neighbors(self, cell: Cell, *, invert=False) -> Iterator[tuple[str, Cell]]:
        with suppress(LookupError):
            xy = cell.row, cell.col - 1
            yield "right" if invert else "left", self[xy]
        with suppress(LookupError):
            xy = cell.row, cell.col + 1
            yield "left" if invert else "right", self[xy]
        with suppress(LookupError):
            xy = cell.row - 1, cell.col
            yield "down" if invert else "up", self[xy]
        with suppress(LookupError):
            xy = cell.row + 1, cell.col
            yield "up" if invert else "down", self[xy]

    def reset(self, size: int):
        assert size <= 5  # see board.html width limits
        self.cells = []
        for row in range(size):
            for col in range(size):
                self.cells.append(Cell(row, col, size=size))

    def initialize(self):
        self[(0, 0)].color = Color.BLUE
        self[(0, 0)].center = 1
        self[(self.size - 1, self.size - 1)].color = Color.RED
        self[(self.size - 1, self.size - 1)].center = 1
        self[(0, self.size - 1)].color = Color.GREEN
        self[(0, self.size - 1)].center = 1
        self[(self.size - 1, 0)].color = Color.YELLOW
        self[(self.size - 1, 0)].center = 1

    def advance(self) -> int:
        count = 0
        for move in chain(
            self.tactical_moves,
            self.border_clashes,
            self.mass_attacks,
            self.attacks,
            self.tactical_moves,
        ):
            move.perform()
            count += 1

        s = "" if count == 1 else "s"
        log.info(f"Applied {count} move{s}")
        return count

    def fortify(self, player: Player):
        cells = list(self.get_cells(player.color))
        cells.sort(key=lambda x: x.value, reverse=True)
        if any(cells):
            extra = max(1, int(len(cells) * EXTRA))
            s = "" if extra == 1 else "s"
            log.info(f"Fortifying {player} with {extra} unit{s}")
            while extra:
                for cell in cells:
                    if extra:
                        log.info(f"+1 {cell}")
                        cell.center += 1
                        extra -= 1
        elif not player.autoplay:
            log.info(f"{player.color.title} player eliminated")
            player.autoplay = True


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

    @cached_property
    def over(self) -> str:
        remaining = [p for p in self.players if any(self.board.get_cells(p.color))]
        if len(remaining) == 1:
            return remaining[0].color.title
        return ""

    @property
    def message(self) -> str:
        if self.round == 0:
            return ""
        if self.over:
            return f"{self.over} player wins!"
        if self.choosing:
            s = "" if self.choosing == 1 else "s"
            return f"Waiting for {self.choosing} player{s} to pick a color..."
        if self.planning:
            s = "" if self.planning == 1 else "s"
            return f"Waiting for {self.planning} player{s} to plan moves..."
        return ""

    def initialize(self, size: int = SIZE, count: int = PLAYERS):
        self.players = Player.defaults()
        if count == 1:
            self.players = self.players[:2]
            self.players[-1].autoplay = True
        else:
            self.players = self.players[:count]

        units: dict[Color, int] = {player.color: UNITS for player in self.players}
        cells: dict[Color, list[Cell]] = {player.color: [] for player in self.players}

        with datafiles.frozen(self):
            self.board.reset(size)
            self.board.initialize()

            for cell in self.board.cells:
                if cell.color is Color.NONE and random.random() < FILL:
                    player = random.choice(self.players)
                    cell.color = player.color
                    cell.center = 1
                    units[player.color] -= 1
                    cells[player.color].append(cell)
                elif cell.color in cells:
                    units[cell.color] -= 1
                    cells[cell.color].append(cell)

            for color, count in units.items():
                for _ in range(count):
                    cell = random.choice(cells[color])
                    cell.center += 1

    def advance(self) -> int:
        count = self.board.advance()
        self.round += 1
        for player in self.players:
            self.board.fortify(player)
        return count

    def get_player(self, color: str) -> Player:
        _color = Color[color.upper()]
        for player in self.players:
            if player.color is _color:
                return player
        raise ValueError(f"Unknown player color: {color}")
