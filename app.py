from flask import Flask, render_template, redirect, url_for
from datafiles import datafile, field
import datafiles
from enum import Enum
import random
from typing import Iterator


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
        return self.value > 0

    def move(self, count: int, direction: str):
        with datafiles.frozen():
            if direction == "center":
                self.reset()
            elif self.value:
                self.value -= count
                value = getattr(self, direction)
                setattr(self, direction, value + count)
        self.datafile.save()

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
        with datafiles.frozen():
            self.board.reset()
            for cell in self.board.cells:
                p = random.randint(1, 4)
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
        self.datafile.save()


@app.get("/games")
def games():
    number = sum(1 for _ in Game.objects.all()) + 1
    game = Game(number)
    game.initialize()
    return redirect(url_for("game", number=number))


@app.get("/games/<int:number>")
def game(number: int):
    game = Game(number)
    return render_template("game.html", game=game)


@app.post("/games/<int:number>/_randomize")
def game_randomize(number: int):
    game = Game(number)
    assert game.round == 0
    game.initialize()
    return render_template("game.html", game=game)


@app.post("/games/<int:number>/_start")
def game_start(number: int):
    game = Game(number)
    game.round = 1
    return render_template("game.html", game=game)


@app.get("/games/<int:number>/_board")
def board(number: int):
    game = Game(number)
    return render_template("board.html", game=game)


@app.post("/games/<int:number>/_cell/<int:row>/<int:col>")
def cell(number: int, row: int, col: int):
    game = Game(number)
    cell = game.board[row, col]
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.post("/games/<int:number>/_cell/<int:row>/<int:col>/<string:direction>")
def move(number: int, row: int, col: int, direction: str):
    game = Game(number)
    cell = game.board[row, col]
    cell.move(1, direction)
    return render_template("cell.html", game=game, cell=cell, editing=True)
