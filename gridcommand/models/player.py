"""Classes representing players in a game."""

from flask import url_for  # TODO: remove this import
import yorm

from ..common import logger
from .turn import Turns


log = logger(__name__)


@yorm.attr(color=yorm.converters.String)
@yorm.attr(code=yorm.converters.String)
@yorm.attr(turns=Turns)
class Player(yorm.converters.AttributeDictionary):

    """An entity that plans moves during a turn."""

    def __init__(self, color, code=''):
        super().__init__()
        self.color = color
        self.code = code
        self.turns = Turns()

    def __repr__(self):
        return "<player: {}>".format(self.color)

    def __eq__(self, other):
        return self.color == other.color

    def authenticate(self, code, exc=ValueError):
        if code != self.code:
            raise exc("The code '{}' is invalid.".format(code))

    def serialize(self, game, auth=False):
        data = {'turn': len(self.turns)}
        kwargs = dict(_external=True, key=game.key, color=self.color)
        if auth:
            kwargs.update(code=self.code)
            player_url = url_for('.players_detail', **kwargs)
            turns_url = url_for('.turns_list', **kwargs)
            data['turns'] = turns_url
        else:
            player_url = url_for('.players_detail', **kwargs)
        data['uri'] = player_url
        return data


@yorm.attr(all=Player)
class Players(yorm.converters.List):

    """A collection players in a game."""

    COLORS = (
        'red',
        'blue',
        'teal',
        'purple',
        'yellow',
        'orange',
        'green',
        'pink',
    )

    def __repr__(self):
        return "<{} player{}>".format(len(self), "" if len(self) == 1 else "s")

    @property
    def maximum(self):
        return len(self.COLORS)

    def serialize(self, game):
        return [url_for('.players_detail', _external=True,
                        key=game.key, color=player.color) for player in self]

    def create(self, code='', exc=RuntimeError):
        log.info("creating player with code %r...", code)
        colors = [player.color for player in self]
        for color in self.COLORS:
            if color not in colors:
                player = Player(color, code=code)
                self.append(player)
                return player
        raise exc("The maximum number of players is {}.".format(self.maximum))

    def find(self, color, exc=ValueError):
        for player in self:
            if player.color == color:
                return player
        if exc:
            raise exc("The player '{}' does not exist.".format(color))

    def delete(self, color):
        player = self.find(color, exc=None)
        if player:
            self.remove(player)
