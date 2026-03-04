import random

from snake_game.board import TickResult
from snake_game.direction import Direction
from snake_game.game_state import GameState, Phase


class TestGameStateInit:
    def test_starts_in_waiting_phase(self):
        gs = GameState(rng=random.Random(42))
        assert gs.phase == Phase.WAITING

    def test_initial_score_is_zero(self):
        gs = GameState(rng=random.Random(42))
        assert gs.score == 0

    def test_initial_speed_is_1(self):
        gs = GameState(rng=random.Random(42))
        assert gs.speed == 1


class TestGameStateTransitions:
    def test_start_game_transitions_to_playing(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        assert gs.phase == Phase.PLAYING

    def test_cannot_start_while_playing(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        gs.start()  # should be ignored
        assert gs.phase == Phase.PLAYING

    def test_death_transitions_to_game_over(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        # Force death by moving into wall
        gs.board.apple = (0, 0)  # move apple away
        for _ in range(3):
            gs.tick(Direction.RIGHT)
        result = gs.tick(Direction.RIGHT)  # hits right wall
        assert result == TickResult.DEATH
        assert gs.phase == Phase.GAME_OVER

    def test_restart_from_game_over(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        gs.board.apple = (0, 0)
        for _ in range(3):
            gs.tick(Direction.RIGHT)
        gs.tick(Direction.RIGHT)  # death
        assert gs.phase == Phase.GAME_OVER
        gs.start()  # restart
        assert gs.phase == Phase.PLAYING
        assert gs.score == 0
        assert gs.speed == 1


class TestGameStateScoring:
    def test_apple_gives_1_point(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        gs.board.apple = (5, 3)
        result = gs.tick(Direction.RIGHT)
        assert result == TickResult.ATE_APPLE
        assert gs.score == 1

    def test_star_gives_3_points(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        gs.board.apple = (0, 0)
        gs.board.star = (5, 3)
        gs.board.star_turns_remaining = 20
        result = gs.tick(Direction.RIGHT)
        assert result == TickResult.ATE_STAR
        assert gs.score == 3

    def test_speed_increases_at_10_points(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        assert gs.speed == 1
        gs.score = 9
        gs.board.apple = (5, 3)
        gs.tick(Direction.RIGHT)  # score becomes 10
        assert gs.score == 10
        assert gs.speed == 2

    def test_speed_increases_at_20_points(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        gs.score = 19
        gs.board.apple = (5, 3)
        gs.tick(Direction.RIGHT)  # score becomes 20
        assert gs.score == 20
        assert gs.speed == 3

    def test_speed_formula(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        # speed = score // 10 + 1
        gs.score = 0
        gs._update_speed()
        assert gs.speed == 1
        gs.score = 10
        gs._update_speed()
        assert gs.speed == 2
        gs.score = 25
        gs._update_speed()
        assert gs.speed == 3


class TestGameStateTick:
    def test_tick_while_waiting_is_noop(self):
        gs = GameState(rng=random.Random(42))
        result = gs.tick(Direction.RIGHT)
        assert result is None

    def test_tick_while_game_over_is_noop(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        gs.board.apple = (0, 0)
        for _ in range(3):
            gs.tick(Direction.RIGHT)
        gs.tick(Direction.RIGHT)  # death
        result = gs.tick(Direction.RIGHT)
        assert result is None


class TestGameStateTickInterval:
    def test_tick_interval_decreases_with_speed(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        interval_speed_1 = gs.tick_interval_ms()
        gs.score = 10
        gs._update_speed()
        interval_speed_2 = gs.tick_interval_ms()
        assert interval_speed_2 < interval_speed_1

    def test_tick_interval_is_positive(self):
        gs = GameState(rng=random.Random(42))
        gs.start()
        for score in [0, 10, 50, 100]:
            gs.score = score
            gs._update_speed()
            assert gs.tick_interval_ms() > 0
