"""Formats domain objects for route responses."""

from collections import OrderedDict

from flask import url_for

from .base import Formatter


# TODO: figure out a better way to serialize objects without parent objects
# pylint: disable=W0221


class GameFormatter(Formatter):

    """Serializes games into dictionaries."""

    def format_single(self, game):
        kwargs = dict(_external=True, key=game.key)
        game_url = url_for('.games_detail', **kwargs)
        players_url = url_for('.players_list', **kwargs)
        start_url = url_for('.games_start', **kwargs)
        return {'uri': game_url,
                'stamp': game.time,
                'players': players_url,
                'start': start_url,
                'turn': game.turn}

    def format_multiple(self, games):
        return [url_for('.games_detail',
                        _external=True, key=key) for key in games]


class PlayerFormatter(Formatter):

    """Serializes players into dictionaries."""

    def format_single(self, player, game, auth):
        data = OrderedDict()
        kwargs = dict(_external=True, key=game.key, color=player.color)
        if auth:
            kwargs.update(code=player.code)
        data['uri'] = url_for('.players_detail', **kwargs)
        data['turns'] = url_for('.turns_list', **kwargs)
        return data

    def format_multiple(self, players, game):
        return [url_for('.players_detail', _external=True,
                        key=game.key, color=player.color) for player in players]


class BoardFormatter(Formatter):

    def format_single(self, board):
        # TODO: format board
        print(board)
        return {}


class TurnFormatter(Formatter):

    """Serializes turns into dictionaries."""

    def format_single(self, turn, game, player, number):
        kwargs = dict(_external=True,
                      key=game.key,
                      color=player.color,
                      code=player.code,
                      number=number)
        turn_url = url_for('.turns_detail', **kwargs)
        moves_url = url_for('.moves_list', **kwargs)
        return {'uri': turn_url,
                'moves': moves_url,
                'done': turn.done}

    def format_multiple(self, turns, game, player):
        return [url_for('.turns_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        number=index + 1) for index in range(len(turns))]


class MoveFormatter(Formatter):

    """Serializes moves into dictionaries."""

    def format_single(self, move):
        return {'count': move.count}

    def format_multiple(self, moves, game, player):
        return [url_for('.moves_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        begin=move.begin, end=move.end) for move in moves]


game_formatter = GameFormatter()
player_formatter = PlayerFormatter()
board_formatter = BoardFormatter()
turn_formatter = TurnFormatter()
move_formatter = MoveFormatter()
