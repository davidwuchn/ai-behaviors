import random
from enum import Enum, auto

from snake_game.direction import Direction

BOARD_WIDTH = 8
BOARD_HEIGHT = 8
STAR_LIFETIME = 20
STAR_GROWTH = 3
STAR_SPAWN_CHANCE = 0.05


class TickResult(Enum):
    MOVED = auto()
    ATE_APPLE = auto()
    ATE_STAR = auto()
    DEATH = auto()


class Board:
    """8x8 snake game board.

    Invariants:
        - apple is always on the board and not on the snake (while alive)
        - at most 1 star on the board
        - star_turns_remaining >= 0
        - snake segments are all within bounds and unique (while alive)
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT

        # Snake: list of (x, y) positions, head first.
        # Starts size 3 in the middle, moving right.
        # Head at (4, 3), body extends left.
        self.snake: list[tuple[int, int]] = [(4, 3), (3, 3), (2, 3)]

        self.star: tuple[int, int] | None = None
        self.star_turns_remaining: int = 0

        self.apple: tuple[int, int] | None = None
        self._spawn_apple()

        self._pending_growth: int = 0

        self._assert_invariants()

    def tick(self, direction: Direction) -> TickResult:
        """Advance the game by one step in the given direction.

        Pre: direction is a valid Direction.
        Post: snake has moved one step; apple/star state updated;
              returns appropriate TickResult.
        """
        assert isinstance(direction, Direction), (
            f"Pre violated: direction must be Direction, got {type(direction)}"
        )

        dx, dy = direction.delta()
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        nx, ny = new_head
        if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
            return TickResult.DEATH

        # Determine what we will eat (before moving, to count growth this tick)
        result = TickResult.MOVED
        if new_head == self.apple:
            self._pending_growth += 1
            result = TickResult.ATE_APPLE
        elif self.star is not None and new_head == self.star:
            self._pending_growth += STAR_GROWTH
            result = TickResult.ATE_STAR

        # Check self collision (against current body, excluding tail that will move)
        # If we're growing this tick, the tail stays — check full body.
        will_grow = self._pending_growth > 0
        body_to_check = self.snake if will_grow else self.snake[:-1]
        if new_head in body_to_check:
            return TickResult.DEATH

        # Move: add new head
        self.snake.insert(0, new_head)

        # Handle growth
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.snake.pop()

        # Finalize eating side effects
        if result == TickResult.ATE_APPLE:
            self._spawn_apple()
        elif result == TickResult.ATE_STAR:
            self.star = None
            self.star_turns_remaining = 0

        # Star countdown
        if self.star is not None:
            self.star_turns_remaining -= 1
            if self.star_turns_remaining <= 0:
                self.star = None
                self.star_turns_remaining = 0

        # Maybe spawn star
        if self.star is None and self._rng.random() < STAR_SPAWN_CHANCE:
            self._spawn_star()

        self._assert_invariants()
        return result

    def _occupied_cells(self) -> set[tuple[int, int]]:
        cells = set(self.snake)
        if self.apple is not None:
            cells.add(self.apple)
        if self.star is not None:
            cells.add(self.star)
        return cells

    def _free_cells(self) -> list[tuple[int, int]]:
        occupied = self._occupied_cells()
        return [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in occupied
        ]

    def _spawn_apple(self) -> None:
        """Spawn apple on a free cell.

        Post: apple is on the board and not on the snake.
        """
        free = self._free_cells()
        assert len(free) > 0, "No free cells to spawn apple"
        self.apple = self._rng.choice(free)
        assert self.apple not in self.snake, "Post violated: apple spawned on snake"

    def _spawn_star(self) -> None:
        """Spawn star on a free cell.

        Pre: no star currently on board.
        Post: star is on the board, not on snake or apple, with full lifetime.
        """
        assert self.star is None, "Pre violated: star already exists"
        free = self._free_cells()
        if not free:
            return
        self.star = self._rng.choice(free)
        self.star_turns_remaining = STAR_LIFETIME
        assert self.star not in self.snake, "Post violated: star spawned on snake"
        assert self.star != self.apple, "Post violated: star spawned on apple"

    def _assert_invariants(self) -> None:
        assert self.apple is not None, "Invariant violated: apple must always be on board"
        ax, ay = self.apple
        assert 0 <= ax < self.width and 0 <= ay < self.height, (
            f"Invariant violated: apple {self.apple} out of bounds"
        )
        assert self.apple not in self.snake, (
            f"Invariant violated: apple {self.apple} is on snake"
        )

        if self.star is not None:
            sx, sy = self.star
            assert 0 <= sx < self.width and 0 <= sy < self.height, (
                f"Invariant violated: star {self.star} out of bounds"
            )
            assert self.star_turns_remaining > 0, (
                "Invariant violated: star present but turns_remaining <= 0"
            )

        assert self.star_turns_remaining >= 0, (
            f"Invariant violated: star_turns_remaining={self.star_turns_remaining} < 0"
        )

        for x, y in self.snake:
            assert 0 <= x < self.width and 0 <= y < self.height, (
                f"Invariant violated: snake segment ({x}, {y}) out of bounds"
            )

        assert len(self.snake) == len(set(self.snake)), (
            "Invariant violated: snake has duplicate segments"
        )
