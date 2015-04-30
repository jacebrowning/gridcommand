"""Classes representing turns in a game."""

from flask import url_for  # TODO: remove this import
import yorm

from .move import Moves


@yorm.attr(moves=Moves)
@yorm.attr(done=yorm.converters.Boolean)
class Turn(yorm.converters.AttributeDictionary):

    """An individual turn for a player."""

    def __init__(self):
        super().__init__()
        self.moves = Moves()
        self.done = False

    def __repr__(self):
        return "<turn>"

    def serialize(self, game, player, number):
        kwargs = dict(_external=True,
                      key=game.key,
                      color=player.color,
                      code=player.code,
                      number=number)
        turn_url = url_for('.turns_detail', **kwargs)
        moves_url = url_for('.moves_list', **kwargs)
        return {'uri': turn_url,
                'moves': moves_url,
                'done': self.done}


@yorm.attr(all=Turn)
class Turns(yorm.converters.List):

    """A list of turns in a game for each player."""

    def __repr__(self):
        return "<{} turn{}>".format(len(self), "" if len(self) == 1 else "s")

    @property
    def current(self):
        """Get the most recent turn."""
        try:
            return self[-1]
        except IndexError:
            return None

    def find(self, number, exc=ValueError):
        try:
            return self[number - 1]
        except IndexError:
            raise exc("The turn '{}' does not exist.".format(number))

    def serialize(self, game, player):

        return [url_for('.turns_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        number=index + 1) for index in range(len(self))]
