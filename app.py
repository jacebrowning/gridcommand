import random
from enum import Enum
from typing import Iterator

import datafiles
import log
from datafiles import datafile, field
from flask import Flask, redirect, render_template, request, url_for

SIZE = 5
UNITS = SIZE * 4
FILL = 2 / 3

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


class State(Enum):
    UNKNOWN = None
    READY = "ready"
    PLANNING = "planning"
    WAITING = "waiting"


@datafile
class Player:
    color: Color
    round: int = 0
    state: State = State.UNKNOWN


@datafile
class Cell:
    row: int
    col: int

    color: Color = Color.NONE

    value: int = 0

    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0

    def __bool__(self):
        return self.color is not Color.NONE

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
        if self.value:
            with datafiles.frozen(self):
                self.value -= count
                value = getattr(self, direction)
                setattr(self, direction, value + count)

    def reset(self):
        with datafiles.frozen(self):
            self.value = self.value + self.up + self.down + self.left + self.right
            self.up = self.down = self.left = self.right = 0


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

    def __getitem__(self, xy) -> Cell:
        row, col = xy
        for cell in self.cells:
            if cell.row == row and cell.col == col:
                return cell
        raise LookupError(f"Unknown cell: {xy}")

    def reset(self):
        self.cells = []
        for row in range(SIZE):
            for col in range(SIZE):
                self.cells.append(Cell(row, col))


@datafile("data/games/{self.number}.yml", defaults=True)
class Game:

    number: int

    round: int = 0
    players: list[Player] = field(
        # TODO: Support more than two players
        default_factory=lambda: [Player(Color.BLUE), Player(Color.RED)]
    )
    board: Board = Board()

    @property
    def waiting(self) -> int:
        return sum(1 for p in self.players if p.state is State.PLANNING)

    @property
    def message(self) -> str:
        count = self.waiting
        s = "" if count == 1 else "s"
        return f"Waiting for {count} other player{s}..."

    def initialize(self):
        units = {player.color: UNITS for player in self.players}
        cells = {player.color: [] for player in self.players}
        with datafiles.frozen(self):
            self.board.reset()
            for cell in self.board.cells:
                if random.random() < FILL:
                    player = random.choice(self.players)
                    cell.color = player.color
                    cell.value = 1
                    units[player.color] -= 1
                    cells[player.color].append(cell)
            for color, count in units.items():
                for _ in range(count):
                    cell = random.choice(cells[color])
                    cell.value += 1

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
    number = sum(1 for _ in Game.objects.all()) + 1
    game = Game(number)
    game.initialize()
    return redirect(url_for("setup", number=number))


@app.get("/game/<int:number>/")
def setup(number: int):
    game = Game(number)
    return render_template("game.html", game=game)


@app.post("/game/<int:number>/_randomize/")
def randomize(number: int):
    game = Game(number)
    assert game.round == 0
    game.initialize()
    return render_template("board.html", game=game)


@app.get("/game/<int:number>/player/")
def players(number: int):
    game = Game(number)
    if "partial" in request.args:
        return render_template("players.html", game=game)
    game.round = 1
    return render_template("game.html", game=game)


@app.get("/game/<int:number>/player/<color>/")
def player(number: int, color: str):
    game = Game(number)
    player = game.get_player(color)
    with datafiles.frozen(player):
        player.round = game.round
        player.state = State.READY
    return render_template("game.html", game=game, player=player)


@app.get("/game/<int:number>/player/<color>/moves/")
def player_moves(number: int, color: str):
    game = Game(number)
    player = game.get_player(color)
    player.state = State.PLANNING
    return render_template("game.html", game=game, player=player)


@app.get("/game/<int:number>/player/<color>/done/")
def player_done(number: int, color: str):
    game = Game(number)
    player = game.get_player(color)
    player.state = State.WAITING
    return render_template("game.html", game=game, player=player)


@app.post("/game/<int:number>/_cell/<int:row>/<int:col>/")
def cell(number: int, row: int, col: int):
    game = Game(number)
    cell = game.board[row, col]
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.post("/game/<int:number>/_cell/<int:row>/<int:col>/<direction>/")
def move(number: int, row: int, col: int, direction: str):
    game = Game(number)
    cell = game.board[row, col]
    if direction == "center":
        cell.reset()
    else:
        cell.move(1, direction)
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.get("/game/<int:number>/_done/<color>")
def done(number: int, color: str):
    game = Game(number)
    player = game.get_player(color)
    if player.round == game.round:
        with datafiles.frozen(game):
            for cell in game.board.cells:
                # TODO: Process moves
                cell.up = cell.down = cell.left = cell.right = 0
        game.round += 1
    return redirect(url_for("player", number=game.number, color=player.color.key))


if __name__ == "__main__":
    from livereload import Server

    app.debug = True
    server = Server(app.wsgi_app)
    server.watch("*.py")
    server.watch("templates")
    server.watch("data", ignore=lambda _: True)
    server.serve(port=5000)
