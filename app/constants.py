import random

SIZE = 3
UNITS = SIZE * 4
FILL = 2 / 3

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
