import math
import random
import time
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain
from typing import Iterator

import datafiles
import log
from flask import url_for

from . import autoplay
from .actions import Attack, AttackWithRetreat, BorderClash, Fortification, MassAttack
from .constants import EXTRA, FILL, PLAYERS, SHARED, SIZE, generate_code
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
    def width(self) -> str:
        return f"{100 / self.size}%"

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
                if move := AttackWithRetreat(start, direction, finish):
                    yield move
        for start in self.cells:
            for direction, finish in self.get_neighbors(start):
                if move := Attack(start, direction, finish):  # type: ignore
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

    def apply_tactical(self) -> int:
        count = 0
        for move in self.tactical_moves:
            move.perform()
            count += 1

        s = "" if count == 1 else "s"
        log.info(f"Applied {count} tactical move{s}")
        return count

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

    def reinforcement_count(self, player: Player) -> int:
        cells = list(self.get_cells(player.color))
        if not cells:
            return 0
        return max(1, int(len(cells) * EXTRA))

    def plan_reinforcements(self, player: Player) -> int:
        """Mark pending reinforcement units on cells without applying them yet."""
        cells = list(self.get_cells(player.color))
        cells.sort(key=lambda x: x.value, reverse=True)
        for cell in cells:
            cell.extra = 0
        extra = self.reinforcement_count(player)
        if extra:
            s = "" if extra == 1 else "s"
            log.info(f"Planning {extra} reinforcement{s} for {player}")
            remaining = extra
            while remaining:
                for cell in cells:
                    if remaining:
                        cell.extra += 1
                        remaining -= 1
            return extra
        if not player.autoplay:
            log.info(f"{player.color.title} player eliminated")
            player.autoplay = True
        return 0

    def fortify(self, player: Player):
        cells = list(self.get_cells(player.color))
        pending = sum(cell.extra for cell in cells)
        if pending:
            s = "" if pending == 1 else "s"
            log.info(f"Fortifying {player} with {pending} unit{s}")
            for cell in cells:
                if cell.extra:
                    log.info(f"+{cell.extra} {cell}")
                    cell.center += cell.extra
                    cell.extra = 0
        elif not player.autoplay and not cells:
            log.info(f"{player.color.title} player eliminated")
            player.autoplay = True


@datafiles.datafile("../data/games/{self.code}.yml", defaults=True)
class Game:

    code: str = field(default_factory=generate_code)

    round: int = 0
    players: list[Player] = field(default_factory=Player.defaults)
    shared: bool = SHARED
    fill: bool = False
    phase: str = ""
    board: Board = field(default_factory=Board)

    @cached_property
    def url(self) -> str:
        return url_for("setup", code=self.code, _external=True)

    @property
    def humans(self) -> list[Player]:
        return [player for player in self.players if not player.autoplay]

    @property
    def living(self) -> list[Player]:
        return [p for p in self.players if any(self.board.get_cells(p.color))]

    @property
    def choosing(self) -> int:
        return sum(1 for p in self.players if p.state is State.UNKNOWN)

    @property
    def planning(self) -> int:
        count = 0
        for player in self.living:
            if player.state is not State.WAITING:
                log.info(f"Waiting for {player} to plan their moves")
                count += 1
            elif player.round < self.round:
                log.info(f"Waiting for {player} to advance the game")
                count += 1
        return count

    @property
    def over(self) -> str:
        remaining = self.living
        if len(remaining) == 1:
            return remaining[0].color.title
        return ""

    @property
    def step(self) -> int:
        if self.phase in {"reinforcements", "reinforce"}:
            return 3
        if self.phase == "results":
            return 2
        return 1

    @property
    def message(self) -> str:
        if self.round == 0:
            return "Choose options for a new game..."
        if self.over:
            return f"{self.over} player wins!"
        if self.choosing:
            s = "" if self.choosing == 1 else "s"
            return f"Waiting for {self.choosing} player{s} to pick a color..."
        if self.planning:
            s = "" if self.planning == 1 else "s"
            return f"Waiting for {self.planning} player{s} to plan moves..."
        if not self.phase:
            return "All players have submitted moves!"
        return ""

    def initialize(self, size: int = SIZE, players: int = PLAYERS):
        self.players = Player.defaults(players)

        units: dict[Color, int] = {player.color: size * 3 for player in self.players}
        cells: dict[Color, list[Cell]] = {player.color: [] for player in self.players}

        with datafiles.frozen(self):
            self.board.reset(size)
            self.board.initialize()

            for cell in self.board.cells:
                if cell.color in cells:
                    units[cell.color] -= 1
                    cells[cell.color].append(cell)

            if self.fill:
                empty = [cell for cell in self.board.cells if cell.color is Color.NONE]
                random.shuffle(empty)
                for player in self.players:
                    while len(cells[player.color]) < 2 and empty:
                        cell = empty.pop()
                        cell.color = player.color
                        cell.center = 1
                        units[player.color] -= 1
                        cells[player.color].append(cell)
                for cell in empty:
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

    def _humans_done_planning(self) -> bool:
        for player in self.humans:
            if not any(self.board.get_cells(player.color)):
                continue
            if player.state is not State.WAITING or player.round < self.round:
                return False
        return True

    def _eliminate_dead_players(self) -> None:
        for player in self.players:
            if any(self.board.get_cells(player.color)):
                continue
            if not player.autoplay:
                log.info(f"{player.color.title} player eliminated")
                player.autoplay = True
            player.state = State.WAITING
            player.round = self.round

    def tick_autoplay(self, *, force: bool = False) -> None:
        """Schedule or finish computer moves in seat order around the table."""
        if not force and (
            self.round < 1 or self.choosing or not self._humans_done_planning()
        ):
            return
        now = time.time()
        humans = len(self.humans)
        computers = [player for player in self.players if player.autoplay]
        for position, player in enumerate(computers):
            if player.round >= self.round:
                continue
            if force:
                self._complete_autoplay(player)
                continue
            if not player.autoplay_until:
                autoplay.schedule(player, position=position, humans=humans, now=now)
                if not autoplay.due(player, now=now):
                    continue
            elif not autoplay.due(player, now=now):
                continue
            self._complete_autoplay(player)

    def tick(self) -> None:
        """Progress computer turns; when no humans remain, advance resolve phases."""
        if self.round < 1 or self.over:
            return
        self.tick_autoplay()
        if any(not player.autoplay for player in self.living):
            return
        if self.planning:
            return
        if not self.phase:
            self.show_results()
        elif self.phase == "results":
            self.show_reinforcements()
        elif self.phase in {"reinforcements", "reinforce"}:
            self.advance()

    def _complete_autoplay(self, player: Player) -> None:
        cells = list(self.board.get_cells(player.color))
        autoplay.plan(cells, player, board=self.board.cells)
        player.state = State.WAITING
        player.round = self.round
        player.autoplay_until = 0.0

    def show_results(self) -> int:
        """Resolve all planned moves (tactical + combat)."""
        path = self.datafile.path.parent / self.code / f"{self.round}.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.datafile.text)

        self.tick_autoplay(force=True)
        count = self.board.advance()
        self._eliminate_dead_players()
        self.phase = "results"
        return count

    def show_reinforcements(self) -> None:
        """Mark pending reinforcements on the board after results are shown."""
        if self.phase != "results":
            self.show_results()
        for player in self.players:
            self.board.plan_reinforcements(player)
        self.phase = "reinforcements"

    def reinforce(self) -> None:
        """Grant reinforcement units after they have been shown."""
        if self.phase != "reinforcements":
            self.show_reinforcements()
        for player in self.players:
            self.board.fortify(player)
        self.phase = "reinforce"

    def advance(self) -> int:
        if self.phase != "reinforce":
            self.reinforce()

        self.round += 1
        self.phase = ""
        return 0

    def get_player(self, color: str) -> Player:
        _color = Color[color.upper()]
        for player in self.players:
            if player.color is _color:
                return player
        raise ValueError(f"Unknown player color: {color}")
