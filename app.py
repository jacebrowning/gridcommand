from flask import Flask, render_template
from datafiles import datafile, field
import datafiles
from enum import Enum
import random
from typing import Iterator

app = Flask(__name__)


class Color(Enum):
    BLUE = "primary"
    RED = "danger"
    GREEN = "success"
    YELLOW = "warning"

    NONE = "light"


@datafile
class Cell:
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
class Row:

    cols: list[Cell] = field(default_factory=lambda: [Cell() for _ in range(5)])


@datafile
class Board:

    rows: list[Row] = field(default_factory=lambda: [Row() for _ in range(5)])

    def __post_init__(self):
        for row_index, row in enumerate(self.rows):
            for col_index, cell in enumerate(row.cols):
                cell.row = row_index
                cell.col = col_index

    def __iter__(self) -> Iterator[Cell]:
        for row in self.rows:
            for cell in row.cols:
                yield cell


@datafile("data/gamess/{self.number}.yml")
class Game:

    number: int
    round: int = 0
    board: Board = Board()

    def initialize(self):
        with datafiles.frozen():
            for cell in self.board:
                p = random.random()
                if 0 < p < 0.25:
                    cell.color = Color.BLUE
                    cell.value = int(p * 10 + 1)
                elif 0.25 < p < 0.5:
                    cell.color = Color.RED
                    cell.value = int(p * 10 + 1)
        self.round = 1


@app.get("/games/<int:number>")
def game(number: int):
    game = Game(number)
    if game.round == 0:
        game.initialize()
    return render_template("game.html", game=game)


@app.get("/games/<int:number>/_board")
def board(number: int):
    game = Game(number)
    return render_template("board.html", game=game)


@app.post("/games/<int:number>/_cell/<int:row>/<int:col>")
def cell(number: int, row: int, col: int):
    game = Game(number)
    cell = game.board.rows[row].cols[col]
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.post("/games/<int:number>/_cell/<int:row>/<int:col>/<string:direction>")
def move(number: int, row: int, col: int, direction: str):
    game = Game(number)
    cell = game.board.rows[row].cols[col]
    cell.move(1, direction)
    return render_template("cell.html", game=game, cell=cell, editing=True)
