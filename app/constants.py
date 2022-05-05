import random

SIZE = 5  # 3 to 5
PLAYERS = 2  # 2 to 4
FILL = 2 / 3  # 0.1 to 1.0
UNITS = SIZE * 4  # 1 to 10

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
