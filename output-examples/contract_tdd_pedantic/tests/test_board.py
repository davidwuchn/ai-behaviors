import random

from snake_game.board import Board, TickResult
from snake_game.direction import Direction


class TestBoardInitialState:
    def test_board_size(self):
        b = Board(rng=random.Random(42))
        assert b.width == 8
        assert b.height == 8

    def test_snake_starts_size_3(self):
        b = Board(rng=random.Random(42))
        assert len(b.snake) == 3

    def test_snake_starts_in_middle_moving_right(self):
        b = Board(rng=random.Random(42))
        # Head should be at center, body extends left
        # Center of 8x8 is (3, 3) or (4, 4) — let's define center as (4, 3)
        # with body at (3, 3), (2, 3) — head first in list
        head = b.snake[0]
        assert head == (4, 3), f"Head should be at (4, 3), got {head}"
        assert b.snake[1] == (3, 3)
        assert b.snake[2] == (2, 3)

    def test_apple_present_on_board(self):
        b = Board(rng=random.Random(42))
        assert b.apple is not None
        ax, ay = b.apple
        assert 0 <= ax < 8
        assert 0 <= ay < 8

    def test_apple_not_on_snake(self):
        b = Board(rng=random.Random(42))
        assert b.apple not in b.snake

    def test_no_star_initially(self):
        b = Board(rng=random.Random(42))
        assert b.star is None


class TestBoardMovement:
    def _board_no_apple_ahead(self):
        """Create a board with the apple moved away from the snake's path."""
        b = Board(rng=random.Random(42))
        b.apple = (0, 0)  # out of the way
        return b

    def test_move_right(self):
        b = self._board_no_apple_ahead()
        result = b.tick(Direction.RIGHT)
        assert result != TickResult.DEATH
        assert b.snake[0] == (5, 3)
        assert len(b.snake) == 3

    def test_move_up(self):
        b = self._board_no_apple_ahead()
        result = b.tick(Direction.UP)
        assert result != TickResult.DEATH
        assert b.snake[0] == (4, 2)

    def test_move_down(self):
        b = self._board_no_apple_ahead()
        result = b.tick(Direction.DOWN)
        assert result != TickResult.DEATH
        assert b.snake[0] == (4, 4)

    def test_move_left_from_up(self):
        b = self._board_no_apple_ahead()
        b.tick(Direction.UP)
        result = b.tick(Direction.LEFT)
        assert result != TickResult.DEATH
        assert b.snake[0] == (3, 2)

    def test_tail_follows(self):
        b = self._board_no_apple_ahead()
        b.tick(Direction.RIGHT)
        # After moving right: head (5,3), body (4,3), (3,3)
        assert b.snake == [(5, 3), (4, 3), (3, 3)]


class TestBoardWallCollision:
    def test_death_on_right_wall(self):
        b = Board(rng=random.Random(42))
        # Head at (4,3), move right 4 times to reach (8,3) which is out of bounds
        # Move 1: (5,3), 2: (6,3), 3: (7,3), 4: (8,3) = death
        for _ in range(3):
            result = b.tick(Direction.RIGHT)
            assert result != TickResult.DEATH
        result = b.tick(Direction.RIGHT)
        assert result == TickResult.DEATH

    def test_death_on_top_wall(self):
        b = Board(rng=random.Random(42))
        # Head at (4,3), move up 4 times: (4,2), (4,1), (4,0), (4,-1) = death
        for _ in range(3):
            result = b.tick(Direction.UP)
            assert result != TickResult.DEATH
        result = b.tick(Direction.UP)
        assert result == TickResult.DEATH

    def test_death_on_left_wall(self):
        b = Board(rng=random.Random(42))
        # Move up first to avoid self-collision, then left
        b.tick(Direction.UP)
        # Head at (4,2), move left: (3,2), (2,2), (1,2), (0,2), (-1,2) = death
        for _ in range(4):
            result = b.tick(Direction.LEFT)
            assert result != TickResult.DEATH
        result = b.tick(Direction.LEFT)
        assert result == TickResult.DEATH

    def test_death_on_bottom_wall(self):
        b = Board(rng=random.Random(42))
        # Head at (4,3), move down: (4,4)...(4,7), (4,8) = death
        for _ in range(4):
            result = b.tick(Direction.DOWN)
            assert result != TickResult.DEATH
        result = b.tick(Direction.DOWN)
        assert result == TickResult.DEATH


class TestBoardSelfCollision:
    def test_death_on_self_collision(self):
        b = Board(rng=random.Random(42))
        # Force a long snake: moving down from (4,3) hits (4,4) which is NOT the tail
        b.snake = [(4, 3), (3, 3), (2, 3), (2, 4), (3, 4), (4, 4), (5, 4)]
        # (4,4) is index 5, tail is (5,4) at index 6 — (4,4) won't vacate
        result = b.tick(Direction.DOWN)
        assert result == TickResult.DEATH


class TestBoardApple:
    def test_eating_apple_grows_snake(self):
        b = Board(rng=random.Random(42))
        # Place apple directly in front of snake
        b.apple = (5, 3)
        result = b.tick(Direction.RIGHT)
        assert result == TickResult.ATE_APPLE
        assert len(b.snake) == 4
        assert b.snake[0] == (5, 3)

    def test_apple_respawns_after_eating(self):
        b = Board(rng=random.Random(42))
        b.apple = (5, 3)
        b.tick(Direction.RIGHT)
        # Apple should have respawned
        assert b.apple is not None
        assert b.apple not in b.snake

    def test_apple_always_on_board(self):
        b = Board(rng=random.Random(42))
        for _ in range(3):
            b.tick(Direction.RIGHT)
        assert b.apple is not None
        ax, ay = b.apple
        assert 0 <= ax < 8
        assert 0 <= ay < 8


class TestBoardStar:
    def test_star_eating_grows_by_3(self):
        b = Board(rng=random.Random(42))
        # Move apple out of the way so star is what gets eaten
        b.apple = (0, 0)
        b.star = (5, 3)
        b.star_turns_remaining = 20
        result = b.tick(Direction.RIGHT)
        assert result == TickResult.ATE_STAR
        # Growth is deferred: +1 this tick, +2 pending over next 2 ticks
        assert len(b.snake) == 4  # 3 + 1 immediate
        b.tick(Direction.RIGHT)
        assert len(b.snake) == 5  # +1 more
        b.tick(Direction.RIGHT)
        assert len(b.snake) == 6  # +1 more = total +3

    def test_star_disappears_after_20_turns(self):
        b = Board(rng=random.Random(42))
        b.star = (0, 0)
        b.star_turns_remaining = 1
        # Tick without going to star
        b.tick(Direction.UP)
        assert b.star is None
        assert b.star_turns_remaining == 0

    def test_star_countdown(self):
        b = Board(rng=random.Random(42))
        b.star = (0, 0)
        b.star_turns_remaining = 5
        b.tick(Direction.UP)
        # Star should still be there with 4 remaining (if we didn't eat it)
        if b.star is not None:
            assert b.star_turns_remaining == 4

    def test_at_most_one_star(self):
        b = Board(rng=random.Random(42))
        # Run many ticks and verify star count never exceeds 1
        directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        for i in range(20):
            d = directions[i % 4]
            result = b.tick(d)
            if result == TickResult.DEATH:
                break
            assert b.star is None or isinstance(b.star, tuple)
            # Can't have more than one star — star is a single value, not a list


class TestBoardInvariants:
    def test_snake_always_within_bounds_during_play(self):
        b = Board(rng=random.Random(42))
        directions = [Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.DOWN]
        for i in range(12):
            d = directions[i % 4]
            result = b.tick(d)
            if result == TickResult.DEATH:
                break
            for x, y in b.snake:
                assert 0 <= x < 8, f"Snake x={x} out of bounds"
                assert 0 <= y < 8, f"Snake y={y} out of bounds"

    def test_no_duplicate_segments_in_snake(self):
        b = Board(rng=random.Random(42))
        directions = [Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.DOWN]
        for i in range(12):
            d = directions[i % 4]
            result = b.tick(d)
            if result == TickResult.DEATH:
                break
            assert len(b.snake) == len(set(b.snake)), "Snake has duplicate segments"
