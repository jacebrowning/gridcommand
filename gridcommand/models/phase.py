"""Classes representing phases in a game."""

from flask import url_for  # TODO: remove this import
import yorm

from .move import Moves


@yorm.attr(moves=Moves)
@yorm.attr(done=yorm.standard.Boolean)
class Phase(yorm.extended.AttributeDictionary):

    """An individual phase for a player."""

    def __init__(self):
        super().__init__()
        self.moves = Moves()
        self.done = False

    def serialize(self, game, player, number):
        moves_url = url_for('.moves_list', _external=True,
                            key=game.key, color=player.color, code=player.code,
                            number=number)
        return {'moves': moves_url,
                'done': self.done}


@yorm.attr(all=Phase)
class Phases(yorm.container.List):

    """A list of phases in a game for each player."""

    def find(self, number, exc=ValueError):
        try:
            return self[number - 1]
        except IndexError:
            raise exc("The phase '{}' does not exist.".format(number))

    def serialize(self, game, player):

        return [url_for('.phases_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        number=index + 1) for index in range(len(self))]
