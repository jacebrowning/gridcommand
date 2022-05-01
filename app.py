import random
from contextlib import suppress
from enum import Enum
from functools import cached_property
from typing import Iterator

import datafiles
from datafiles import datafile, field
from flask import Flask, redirect, render_template, request, url_for

SIZE = 3
UNITS = SIZE * 4
FILL = 2 / 3

LETTERS = "ABCDEFGHJKLMNPQRTUVXYZ"
NUMBERS = "2346789"

app = Flask(__name__)


class Color(Enum):
    BLUE = "primary"
    RED = "danger"
    GREEN = "success"
    YELLOW = "warning"

    NONE = "dark"

    @property
    def key(self) -> str:
        return self.name.lower()

    @property
    def title(self) -> str:
        return self.name.title()

    @property
    def icon(self) -> str:
        values = {
            self.BLUE: "🟦",
            self.RED: "🟥",
            self.GREEN: "🟩",
            self.YELLOW: "🟨",
            self.NONE: "∅",
        }
        return values[self]  # type: ignore


class State(Enum):
    UNKNOWN = None
    READY = "ready"
    PLANNING = "planning"
    WAITING = "waiting"

    @property
    def title(self) -> str:
        return self.name.title()


@datafile
class Player:
    color: Color
    round: int = 0
    state: State = State.UNKNOWN


@datafile(order=True)
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


@datafile
class Move:
    start: Cell
    direction: str
    finish: Cell

    def __str__(self):
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
        return {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }[self.direction]

    @property
    def arrow(self) -> str:
        return {
            "up": "⬆️",
            "down": "⬇️",
            "left": "⬅️",
            "right": "➡️",
            "left-right": "↔",
            "up-down": "↕",
        }[self.direction]

    def perform(self):
        raise NotImplementedError


@datafile
class Fortification(Move):
    def __bool__(self):
        return bool(self.start.color == self.finish.color and self.outgoing)

    def perform(self):
        self.finish.center += self.outgoing
        setattr(self.start, self.direction, 0)


@datafile
class BorderClash(Move):
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
        raise NotImplementedError


@datafile
class Attack(Move):
    def __bool__(self):
        return bool(
            self.start.color != self.finish.color
            and self.outgoing
            and not self.incoming
        )


@datafile
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
                    if direction in {"up", "down"}:
                        direction = "up-down"
                    if direction in {"left", "right"}:
                        direction = "left-right"
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


def generate_code() -> str:
    return "".join(
        [
            random.choice(LETTERS),
            random.choice(NUMBERS),
            random.choice(LETTERS),
            random.choice(NUMBERS),
        ]
    )


@datafile("data/games/{self.code}.yml", defaults=True)
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


@app.context_processor
def constants():
    return dict(Color=Color, State=State)


@app.get("/")
def index():
    return redirect(url_for("create"))


@app.get("/game/")
def create():
    game = Game()
    game.initialize()
    return redirect(url_for("setup", code=game.code))


@app.get("/game/<code>/")
def setup(code: str):
    game = Game(code)
    if game.round:
        return redirect(url_for("choose", code=game.code))
    return render_template("game.html", game=game)


@app.get("/game/<code>.json")
def debug(code: str):
    game = Game(code)
    return game.datafile.data


@app.post("/game/<code>/_randomize/")
def randomize(code: str):
    game = Game(code)
    assert game.round == 0
    game.initialize()
    return render_template("board.html", game=game)


@app.get("/game/<code>/player/")
def choose(code: str):
    game = Game(code)
    game.round = game.round or 1
    if "partial" in request.args:
        return render_template("menu/choose.html", game=game)
    return render_template("game.html", game=game)


@app.get("/game/<code>/player/<color>/")
def player(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    with datafiles.frozen(player):
        if game.round > player.round:
            player.round = game.round
            player.state = State.READY
    return render_template("game.html", game=game, player=player)


@app.post("/game/<code>/player/<color>/_plan/")
def player_plan(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    if "partial" in request.args:
        return render_template("menu/plan.html", game=game, player=player)
    player.state = State.PLANNING
    return render_template("board.html", game=game, player=player)


@app.post("/game/<code>/player/<color>/_done/")
def player_done(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    player.state = State.WAITING
    return render_template("board.html", game=game, player=player)


@app.get("/game/<code>/player/<color>/_next")
def player_next(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    player.state = State.READY
    if player.round == game.round:
        with datafiles.frozen(game):
            move: Move
            for move in game.board.fortifications:
                move.perform()
            for move in game.board.border_clashes:
                move.perform()
            # TODO: Handle mass attacks
            # TODO: Handle spoils of war
            for move in game.board.attacks:
                move.perform()
        game.round += 1
    return redirect(url_for("player", code=game.code, color=player.color.key))


@app.post("/game/<code>/_cell/<int:row>/<int:col>/")
def cell(code: str, row: int, col: int):
    game = Game(code)
    cell = game.board[row, col]
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.post("/game/<code>/_cell/<int:row>/<int:col>/<direction>/")
def move(code: str, row: int, col: int, direction: str):
    game = Game(code)
    cell = game.board[row, col]
    if direction == "center":
        cell.reset()
    else:
        cell.move(1, direction)
    return render_template("cell.html", game=game, cell=cell, editing=True)


if __name__ == "__main__":
    from livereload import Server

    app.debug = True
    server = Server(app.wsgi_app)
    server.watch("*.py")
    server.watch("templates")
    server.watch("data", ignore=lambda _: True)
    server.serve(port=5000)
