"""Data used by the running application."""

import os

from .models import Game, Games


games = Games()  # pylint: disable=C0103


def load():
    """Add previously stored data to the application."""
    _path = os.path.join("data", "games")  # TODO: move this to settings?
    if os.path.exists(_path):
        for filename in os.listdir(_path):
            _key = filename.split('.')[0]
            games[_key] = Game(_key)
