from enum import Enum


class Color(Enum):
    BLUE = "primary"
    RED = "danger"
    GREEN = "success"
    YELLOW = "warning"

    NONE = "dark"

    @property
    def key(self) -> str:
        return self.name.lower()

    @property
    def title(self) -> str:
        return self.name.title()

    @property
    def icon(self) -> str:
        values = {
            self.BLUE: "🟦",
            self.RED: "🟥",
            self.GREEN: "🟩",
            self.YELLOW: "🟨",
            self.NONE: "□",
        }
        return values[self]  # type: ignore


class State(Enum):
    UNKNOWN = None
    READY = "ready"
    PLANNING = "planning"
    WAITING = "waiting"

    @property
    def title(self) -> str:
        return self.name.title()
