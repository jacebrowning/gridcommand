"""Classes representing players in a game."""

from ..common import logger
from .turn import Turns


log = logger(__name__)


class Player:

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
        if not code:
            raise exc("Player code required.")
        if code != self.code:
            raise exc("Player code '{}' is invalid.".format(code))


class Players(list):

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
