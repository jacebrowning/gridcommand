from pathlib import Path

import pytest
from expecter import expect

from app.models import Game
from app.views import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def saved_game():
    game = Game()
    game.initialize()
    game.datafile.save()
    path = Path(game.datafile.path)
    yield game
    path.unlink(missing_ok=True)


def test_join_game_with_code(client, saved_game):
    response = client.post("/game/", data={"code": saved_game.code})

    expect(response.status_code) == 302
    expect(response.headers["Location"]) == f"/game/{saved_game.code}/"


def test_join_game_uppercases_code(client, saved_game):
    response = client.post("/game/", data={"code": saved_game.code.lower()})

    expect(response.status_code) == 302
    expect(response.headers["Location"]) == f"/game/{saved_game.code}/"


def test_join_missing_game_shows_error(client):
    response = client.post("/game/", data={"code": "zzzz"})

    expect(response.status_code) == 200
    expect(b"No game found for code ZZZZ" in response.data) == True
