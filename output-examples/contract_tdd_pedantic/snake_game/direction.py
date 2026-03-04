from enum import Enum


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    def opposite(self) -> "Direction":
        return _OPPOSITES[self]

    def is_opposite(self, other: "Direction") -> bool:
        return self.opposite() is other

    def delta(self) -> tuple[int, int]:
        """Returns (dx, dy) for this direction.

        Postcondition: exactly one of dx, dy is non-zero, and its absolute value is 1.
        """
        result = _DELTAS[self]
        dx, dy = result
        assert (dx == 0) != (dy == 0), f"Invariant violated: delta must have exactly one non-zero component, got {result}"
        assert abs(dx) + abs(dy) == 1, f"Invariant violated: delta magnitude must be 1, got {result}"
        return result

    @staticmethod
    def all() -> list["Direction"]:
        """Returns all four directions.

        Postcondition: exactly 4 directions returned.
        """
        result = list(Direction)
        assert len(result) == 4, f"Invariant violated: expected 4 directions, got {len(result)}"
        return result


_OPPOSITES = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

_DELTAS = {
    Direction.UP: (0, -1),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0),
}
