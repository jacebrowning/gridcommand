import os
import random

SIZE = int(os.getenv("SIZE", "5"))  # 3 to 5
PLAYERS = int(os.getenv("PLAYERS", "4"))  # 2 to 4
FILL = 2 / 3  # 0.1 to 1.0
UNITS = SIZE * 4  # 1 to 10
EXTRA = 1 / 3  # 0.0 to 1.0

LETTERS = "ABCDEFGHJKLMNPQRTUVXYZ"
NUMBERS = "2346789"


def generate_code() -> str:
    return "".join(
        [
            random.choice(LETTERS),
            random.choice(NUMBERS),
            random.choice(LETTERS),
            random.choice(NUMBERS),
        ]
    )
