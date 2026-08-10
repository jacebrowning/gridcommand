import os
import random
import sys

SIZE = int(os.getenv("SIZE", "4"))  # 3 to 5
PLAYERS = int(os.getenv("PLAYERS", "2"))  # 1 to 4
SHARED = os.getenv("SHARED") == "true"

FILL = 2 / 3  # 0.1 to 1.0
UNITS = SIZE * 4  # scales with board size in Game.initialize
EXTRA = 1 / 3  # 0.0 to 1.0

LETTERS = "ABCDEFGHJKLMNPQRTUVXYZ"
NUMBERS = "2346789"

TESTING = "pytest" in sys.modules


def generate_code() -> str:
    return "".join(
        [
            random.choice(LETTERS),
            random.choice(NUMBERS),
            random.choice(LETTERS),
            random.choice(NUMBERS),
        ]
    )
