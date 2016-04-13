"""Classes representing player's moves."""


class Move:
    """A planned transfer of tokens from one cell to another."""

    def __init__(self, begin, end, count=0):
        super().__init__()
        self.begin = begin
        self.end = end
        self.count = count

    def __repr__(self):
        return "<move: {} from {} to {}>".format(self.count,
                                                 self.begin,
                                                 self.end)

    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end

    def __lt__(self, other):
        if self.begin < other.begin:
            return True
        if self.begin > other.begin:
            return False
        return self.end < other.end


class Moves(list):
    """A collection of moves for a player."""

    def __repr__(self):
        return "<{} move{}>".format(len(self), "" if len(self) == 1 else "s")

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
