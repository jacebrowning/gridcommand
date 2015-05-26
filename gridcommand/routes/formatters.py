"""Formats domain objects for route responses."""

from flask import url_for

from .base import Formatter


class GameFormatter(Formatter):

    """Serializes games into dictionaries."""

    def format_single(self, game):
        kwargs = dict(_external=True, key=game.key)
        game_url = url_for('.games_detail', **kwargs)
        players_url = url_for('.players_list', **kwargs)
        start_url = url_for('.games_start', **kwargs)
        return {'uri': game_url,
                'players': players_url,
                'start': start_url,
                'turn': game.turn}

    def format_multiple(self, games):
        return [url_for('.games_detail',
                        _external=True, key=key) for key in games]


class PlayerFormatter(Formatter):

    """Serializes players into dictionaries."""

    def format_single(self, player):
        data = {'turn': len(player.turns)}
        kwargs = dict(_external=True, key=game.key, color=player.color)
        if auth:
            kwargs.update(code=player.code)
            player_url = url_for('.players_detail', **kwargs)
            turns_url = url_for('.turns_list', **kwargs)
            data['turns'] = turns_url
        else:
            player_url = url_for('.players_detail', **kwargs)
        data['uri'] = player_url
        return data

    def format_multiple(self, players, game):
        return [url_for('.players_detail', _external=True,
                        key=game.key, color=player.color) for player in players]


class TurnFormatter(Formatter):

    """Serializes turns into dictionaries."""

    def format_single(self, turn):
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

    def format_multiple(self, turns):
        return [url_for('.turns_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        number=index + 1) for index in range(len(turns))]


class MoveFormatter(Formatter):

    """Serializes moves into dictionaries."""

    def format_single(self, move):
        return {'count': move.count}

    def format_multiple(self, moves):
        return [url_for('.moves_detail', _external=True,
                        key=game.key, color=player.color, code=player.code,
                        begin=move.begin, end=move.end) for move in self]


game_formatter = GameFormatter()
player_formatter = PlayerFormatter()
turn_formatter = TurnFormatter()
move_formatter = MoveFormatter()
