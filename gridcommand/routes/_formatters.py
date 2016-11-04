"""Formats domain objects for route responses."""

from collections import OrderedDict

from flask import url_for

from ._bases import Formatter


# TODO: figure out a better way to serialize objects without parent objects
# pylint: disable=arguments-differ


class GameFormatter(Formatter):
    """Serializes games into dictionaries."""

    def format_single(self, game):
        data = OrderedDict()

        kwargs = dict(_external=True, key=game.key)
        data['uri'] = url_for('games.detail', **kwargs)
        data['key'] = game.key
        data['timestamp'] = game.timestamp
        data['players'] = url_for('players.index', **kwargs)
        data['turn'] = game.turn
        data['pending'] = game.pending
        data['start'] = url_for('games.start', **kwargs)

        return data

    def format_multiple(self, games):
        return [url_for('games.detail',
                        _external=True, key=game.key) for game in games]


class PlayerFormatter(Formatter):
    """Serializes players into dictionaries."""

    def format_single(self, player, game, auth):
        data = OrderedDict()

        kwargs = dict(_external=True, key=game.key, color=player.color)
        if auth:
            kwargs.update(code=player.code)
        data['uri'] = url_for('players.detail', **kwargs)
        data['color'] = player.color
        if auth:
            data['code'] = player.code
        data['done'] = player.turn.done
        if auth:
            data['turns'] = url_for('turns.index', **kwargs)

        return data

    def format_multiple(self, players, game):
        return [url_for('players.detail', _external=True,
                        key=game.key, color=player.color) for player in players]


class BoardFormatter(Formatter):

    def format_single(self, board):
        data = OrderedDict()

        # TODO: format board
        print(board)

        return data


class TurnFormatter(Formatter):
    """Serializes turns into dictionaries."""

    def format_single(self, game, player, number):
        data = OrderedDict()

        kwargs = dict(_external=True,
                      key=game.key,
                      color=player.color,
                      code=player.code,
                      number=number)
        data['uri'] = url_for('turns.detail', **kwargs)
        data['moves'] = url_for('moves.index', **kwargs)
        data['finish'] = url_for('turns.finish', **kwargs)

        return data

    def format_multiple(self, turns, game, player):
        return [url_for('turns.detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        number=index + 1) for index in range(len(turns))]


class MoveFormatter(Formatter):
    """Serializes moves into dictionaries."""

    def format_single(self, move):
        data = OrderedDict()

        data['count'] = move.count

        return data

    def format_multiple(self, moves, game, player):
        return [url_for('moves.detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        begin=move.begin, end=move.end) for move in moves]


game_formatter = GameFormatter()
player_formatter = PlayerFormatter()
board_formatter = BoardFormatter()
turn_formatter = TurnFormatter()
move_formatter = MoveFormatter()
