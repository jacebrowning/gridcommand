"""Classes representing game objects."""

import string
import random

from flask import url_for  # TODO: remove this import
import yorm


@yorm.attr(begin=yorm.standard.Integer)
@yorm.attr(end=yorm.standard.Integer)
@yorm.attr(count=yorm.standard.Integer)
class Move(yorm.extended.AttributeDictionary):

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
class Moves(yorm.extended.SortedList):

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


@yorm.attr(color=yorm.standard.String)
@yorm.attr(code=yorm.standard.String)
@yorm.attr(phases=Phases)
@yorm.attr(done=yorm.standard.Boolean)
class Player(yorm.extended.AttributeDictionary):

    """An entity that plans moves during a phase."""

    def __init__(self, color, code=''):
        super().__init__()
        self.color = color
        self.code = code
        self.phases = Phases()
        self.done = False

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


@yorm.attr(players=Players)
@yorm.attr(phase=yorm.standard.Integer)
@yorm.sync("data/games/{self.key}.yml")
class Game:

    """An individual game instance."""

    KEY_CHARS = string.ascii_lowercase + string.digits
    KEY_LENGTH = 8

    def __init__(self, key=None):
        self.key = key or self._generate_key()
        self.players = Players()
        self.phase = 0

    @staticmethod
    def _generate_key():
        return ''.join(random.choice(Game.KEY_CHARS)
                       for _ in range(Game.KEY_LENGTH))

    def create_player(self, code, exc=ValueError):
        if self.started:
            raise exc("Game has already started.")
        return self.players.create(code, exc=exc)

    def delete_player(self, color, exc=ValueError):
        if self.started:
            raise exc("Game has already started.")
        self.players.delete(color)

    @property
    def started(self):
        return self.phase > 0

    def start(self, exc=ValueError):
        if len(self.players) < 2:
            raise exc("At least 2 players are required.")
        self.phase = self.phase or 1

    def serialize(self):
        kwargs = {'_external': True, 'key': self.key}
        players_url = url_for('.players_list', **kwargs)
        start_url = url_for('.games_start', **kwargs)
        return {'key': self.key,
                'players': players_url,
                'start': start_url,
                'phase': self.phase}


class Games(dict):

    """A collection of all games in the application."""

    def serialize(self):
        return [url_for('.games_detail',
                        _external=True, key=key) for key in self]

    def create(self):
        game = Game()
        self[game.key] = game
        return game

    def find(self, key, exc=ValueError):
        try:
            player = self[key]
        except KeyError:
            raise exc("The game '{}' does not exist.".format(key)) from None
        else:
            return player
