import random
from enum import Enum, auto

from snake_game.board import Board, TickResult
from snake_game.direction import Direction

BASE_INTERVAL_MS = 300
MIN_INTERVAL_MS = 80
INTERVAL_DECREASE_PER_SPEED = 30
POINTS_PER_APPLE = 1
POINTS_PER_STAR = 3
POINTS_PER_SPEED_LEVEL = 10


class Phase(Enum):
    WAITING = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class GameState:
    """Top-level game state machine.

    Invariants:
        - score >= 0
        - speed >= 1
        - speed == score // POINTS_PER_SPEED_LEVEL + 1
        - phase is always a valid Phase
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.phase: Phase = Phase.WAITING
        self.score: int = 0
        self.speed: int = 1
        self.board: Board = Board(rng=self._rng)

    def start(self) -> None:
        """Start or restart the game.

        Pre: phase is WAITING or GAME_OVER.
        Post: phase is PLAYING, score is 0, speed is 1, board is fresh.
        """
        if self.phase == Phase.PLAYING:
            return
        self.phase = Phase.PLAYING
        self.score = 0
        self.speed = 1
        self.board = Board(rng=self._rng)
        self._assert_invariants()

    def tick(self, direction: Direction) -> TickResult | None:
        """Advance one game tick.

        Pre: direction is a valid Direction.
        Post: if PLAYING, board ticked, score/speed updated. Otherwise None.
        """
        if self.phase != Phase.PLAYING:
            return None

        result = self.board.tick(direction)

        if result == TickResult.DEATH:
            self.phase = Phase.GAME_OVER
            return result

        if result == TickResult.ATE_APPLE:
            self.score += POINTS_PER_APPLE
        elif result == TickResult.ATE_STAR:
            self.score += POINTS_PER_STAR

        self._update_speed()
        self._assert_invariants()
        return result

    def _update_speed(self) -> None:
        self.speed = self.score // POINTS_PER_SPEED_LEVEL + 1

    def tick_interval_ms(self) -> int:
        """Milliseconds between ticks at current speed.

        Post: result > 0.
        """
        interval = BASE_INTERVAL_MS - (self.speed - 1) * INTERVAL_DECREASE_PER_SPEED
        result = max(interval, MIN_INTERVAL_MS)
        assert result > 0, f"Post violated: tick_interval_ms must be positive, got {result}"
        return result

    def _assert_invariants(self) -> None:
        assert self.score >= 0, f"Invariant violated: score={self.score} < 0"
        assert self.speed >= 1, f"Invariant violated: speed={self.speed} < 1"
        expected_speed = self.score // POINTS_PER_SPEED_LEVEL + 1
        assert self.speed == expected_speed, (
            f"Invariant violated: speed={self.speed} != expected {expected_speed} "
            f"for score={self.score}"
        )
