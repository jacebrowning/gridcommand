# pylint: disable=W0613,R0201,C0111

import os
import tempfile
import logging

import pytest

from gridcommand.stores import GameMemoryStore, GameFileStore
from gridcommand import domain


@pytest.mark.parametrize("store_class", [GameMemoryStore, GameFileStore])
class TestGameStore:

    def setup_method(self, method):
        path = tempfile.mkdtemp()
        os.chdir(path)

    def test_create_and_read(self, store_class):
        store = store_class()

        game = domain.Game('test_game')
        game.players.append(domain.Player('red'))
        game.players[0].turn = domain.Turn()
        game.players[0].turn.moves.append(domain.Move(0, 0))
        logging.info("creating game...")
        store.create(game)

        logging.info("reading game...")
        game2 = store.read(game.key)
        assert game == game2
        assert game2.turn == 0
        assert game2.players[0].color == 'red'
        assert game2.players[0].turn.done is False
        assert game2.players[0].turn.moves[0].begin == 0

    def test_read_single_unknown(self, store_class):
        store = store_class()

        game = store.read('unknown_key')
        assert game is None

    def test_read_multiple(self, store_class):
        store = store_class()

        game = domain.Game()
        store.create(game)
        game = domain.Game()
        store.create(game)

        games = store.filter()

        assert len(games) == 2

    def test_read_multiple_empty(self, store_class):
        store = store_class()

        games = store.filter()

        assert games == []

    def test_update_existing(self, store_class):
        store = store_class()

        game = domain.Game()
        game = store.create(game)

        game.timestamp = 42
        logging.info("updating game...")
        store.update(game)

        game2 = store.read(game.key)
        assert game2.timestamp == 42

    def test_delete_existing(self, store_class):
        store = store_class()

        game = domain.Game()
        store.create(game)

        store.delete(game)

        game2 = store.read(game.key)
        assert game2 is None

    def test_delete_missing(self, store_class):
        store = store_class()

        game = domain.Game()

        store.delete(game)

        game2 = store.read(game.key)
        assert game2 is None
