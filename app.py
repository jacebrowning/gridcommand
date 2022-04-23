import random
from enum import Enum
from typing import Iterator

import datafiles
from datafiles import datafile, field
from flask import Flask, redirect, render_template, url_for

SIZE = 5
UNITS = 20

app = Flask(__name__)


class Color(Enum):
    BLUE = "primary"
    RED = "danger"
    GREEN = "success"
    YELLOW = "warning"

    NONE = "dark"


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


@datafile("data/games/{self.number}.yml")
class Game:

    number: int

    round: int = 0
    board: Board = Board()

    def initialize(self):
        units = {Color.BLUE: UNITS, Color.RED: UNITS}
        cells = {Color.BLUE: [], Color.RED: []}
        with datafiles.frozen(self):
            self.board.reset()
            for cell in self.board.cells:
                p = random.randint(1, 3)
                if p == 1:
                    cell.color = Color.BLUE
                    cell.value = 1
                    units[Color.BLUE] -= 1
                    cells[Color.BLUE].append(cell)
                elif p == 2:
                    cell.color = Color.RED
                    cell.value = 1
                    units[Color.RED] -= 1
                    cells[Color.RED].append(cell)
            for color, count in units.items():
                for _ in range(count):
                    cell = random.choice(cells[color])
                    cell.value += 1


@app.get("/")
def index():
    return redirect(url_for("game_create"))


@app.get("/game/")
def game_create():
    number = sum(1 for _ in Game.objects.all()) + 1
    game = Game(number)
    game.initialize()
    return redirect(url_for("game_setup", number=number))


@app.get("/game/<int:number>")
def game_setup(number: int):
    game = Game(number)
    return render_template("game.html", game=game)


@app.post("/game/<int:number>/_randomize")
def game_randomize(number: int):
    game = Game(number)
    assert game.round == 0
    game.initialize()
    return render_template("board.html", game=game)


@app.post("/game/<int:number>/_start")
def game_start(number: int):
    game = Game(number)
    game.round = 1
    return render_template("board.html", game=game)


@app.get("/game/<int:number>/player/<color>")
def player(number: int, color: str):
    game = Game(number)
    player = Color[color.upper()]
    return render_template("game.html", game=game, player=player)


@app.post("/game/<int:number>/_cell/<int:row>/<int:col>")
def cell(number: int, row: int, col: int):
    game = Game(number)
    cell = game.board[row, col]
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.post("/game/<int:number>/_cell/<int:row>/<int:col>/<direction>")
def move(number: int, row: int, col: int, direction: str):
    game = Game(number)
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
