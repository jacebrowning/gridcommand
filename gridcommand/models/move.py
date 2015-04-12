"""Classes representing player's moves."""

from flask import url_for  # TODO: remove this import
import yorm


@yorm.attr(begin=yorm.converters.Integer)
@yorm.attr(end=yorm.converters.Integer)
@yorm.attr(count=yorm.converters.Integer)
class Move(yorm.converters.AttributeDictionary):

    """A planned transfer of tokens from one cell to another."""

    def __init__(self, begin, end, count=0):
        super().__init__()
        self.begin = begin
        self.end = end
        self.count = count

    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end

    def __lt__(self, other):
        if self.begin < other.begin:
            return True
        if self.begin > other.begin:
            return False
        return self.end < other.end

    def serialize(self):
        return {'count': self.count}


@yorm.attr(all=Move)
class Moves(yorm.converters.SortedList):

    """A collection of moves for a player."""

    def serialize(self, game, player):
        return [url_for('.moves_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        begin=move.begin, end=move.end) for move in self]

    def get(self, begin, end):
        move = Move(begin, end)
        for move2 in self:
            if move == move2:
                return move2
        self.append(move)
        return move

    def set(self, begin, end, count):
        move = self.get(begin, end)
        if count is not None:
            move.count = count
        if not move.count:
            self.delete(begin, end)
        return move

    def delete(self, begin, end):
        move = Move(begin, end)
        try:
            self.remove(move)
        except ValueError:
            pass
