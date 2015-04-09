"""Classes representing players in a game."""

from flask import url_for  # TODO: remove this import
import yorm

from .phase import Phases


@yorm.attr(color=yorm.standard.String)
@yorm.attr(code=yorm.standard.String)
@yorm.attr(phases=Phases)
class Player(yorm.extended.AttributeDictionary):

    """An entity that plans moves during a phase."""

    def __init__(self, color, code=''):
        super().__init__()
        self.color = color
        self.code = code
        self.phases = Phases()

    def __eq__(self, other):
        return self.color == other.color

    def authenticate(self, code, exc=ValueError):
        if code != self.code:
            raise exc("The code '{}' is invalid.".format(code))

    def serialize(self, game, auth=False):
        data = {'color': self.color,
                'phase': len(self.phases)}
        phases_url = url_for('.phases_list', _external=True,
                             key=game.key, color=self.color, code=self.code)
        if auth:
            data['code'] = self.code
            data['phases'] = phases_url
        return data


@yorm.attr(all=Player)
class Players(yorm.container.List):

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

    @property
    def maximum(self):
        return len(self.COLORS)

    def serialize(self, game):
        return [url_for('.players_detail', _external=True,
                        key=game.key, color=player.color) for player in self]

    def create(self, code='', exc=RuntimeError):
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
