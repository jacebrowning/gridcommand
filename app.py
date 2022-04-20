from flask import Flask, escape, request, render_template
from datafiles import datafile, field


app = Flask(__name__)


@datafile
class Cell:
    color: str = "white"
    count: int = 0


@datafile
class Row:

    cols: list[Cell] = field(default_factory=lambda: [Cell(), Cell(), Cell()])


@datafile
class Board:

    rows: list[Row] = field(default_factory=lambda: [Row(), Row(), Row()])

    def __post_init__(self):
        for row_index, row in enumerate(self.rows):
            for col_index, cell in enumerate(row.cols):
                cell.row = row_index
                cell.col = col_index


@datafile("data/gamess/{self.number}.yml")
class Game:

    number: int
    round: int = 0
    board: Board = Board()


@app.get("/games/<int:number>")
def game(number: int):
    game = Game(number)
    return render_template("game.html", game=game)


@app.get("/games/<int:number>/_board")
def board(number: int):
    game = Game(number)
    return render_template("board.html", game=game)


@app.post("/games/<int:number>/_cell/<int:row>/<int:col>")
def cell(number: int, row: int, col: int):
    game = Game(number)
    cell = game.board.rows[row].cols[col]
    cell.count += 1
    return render_template("cell.html", game=game, cell=cell)
