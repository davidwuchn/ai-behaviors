from game import Game, Direction


def test_initial_snake_is_size_3_in_middle_moving_right():
    g = Game()
    assert len(g.snake) == 3
    assert g.snake[0] == (4, 3)  # head
    assert g.snake[1] == (3, 3)
    assert g.snake[2] == (2, 3)
    assert g.direction == Direction.RIGHT


def test_snake_moves_right():
    g = Game()
    g.tick()
    assert g.snake[0] == (5, 3)
    assert len(g.snake) == 3


def test_change_direction_up():
    g = Game()
    g.queue_direction(Direction.UP)
    g.tick()
    assert g.snake[0] == (4, 2)


def test_cannot_reverse_direction():
    g = Game()
    g.queue_direction(Direction.LEFT)  # opposite of RIGHT
    g.tick()
    assert g.snake[0] == (5, 3)  # still moves right


def test_queued_directions_apply_sequentially():
    g = Game()
    g.queue_direction(Direction.UP)
    g.queue_direction(Direction.LEFT)
    g.tick()
    assert g.snake[0] == (4, 2)  # moved up
    g.tick()
    assert g.snake[0] == (3, 2)  # moved left


def test_queued_reverse_after_turn_is_rejected():
    g = Game()  # moving RIGHT
    g.queue_direction(Direction.UP)
    g.queue_direction(Direction.DOWN)  # would reverse after UP
    g.tick()
    assert g.snake[0] == (4, 2)  # moved up
    g.tick()
    assert g.snake[0] == (4, 1)  # still up, DOWN was rejected


def test_wall_collision_kills():
    g = Game()
    # head at (4,3), moving right. 3 ticks to hit wall at x=8
    g.tick()  # (5,3)
    g.tick()  # (6,3)
    g.tick()  # (7,3)
    assert g.alive
    g.tick()  # (8,3) - out of bounds
    assert not g.alive


def test_self_collision_kills():
    g = Game()
    # Make snake long enough to collide with itself
    # snake: [(4,3),(3,3),(2,3)] moving right
    # Force a tight loop: right, up, left, down => head hits body
    g.snake = [(4, 3), (3, 3), (2, 3), (1, 3), (0, 3)]
    g.queue_direction(Direction.UP)
    g.tick()  # (4,2)
    g.queue_direction(Direction.LEFT)
    g.tick()  # (3,2)
    g.queue_direction(Direction.DOWN)
    g.tick()  # (3,3) - body segment is here
    assert not g.alive


def test_eating_apple_grows_snake_and_scores():
    g = Game()
    g.apple = (5, 3)  # one step right of head
    g.tick()
    assert g.snake[0] == (5, 3)
    assert len(g.snake) == 4  # grew by 1
    assert g.score == 1
    assert g.apple != (5, 3)  # new apple spawned


def test_apple_always_present():
    g = Game()
    g.apple = (5, 3)
    g.tick()  # eat apple
    assert g.apple is not None


def test_star_eating_grows_by_3_and_scores_3():
    g = Game()
    g.star = (5, 3)
    g.star_timer = 10
    g.tick()  # eat star, grow 1 of 3
    assert len(g.snake) == 4
    assert g.score == 3
    assert g.star is None
    assert g.star_timer == 0
    g.queue_direction(Direction.DOWN)
    g.tick()  # grow 2 of 3
    assert len(g.snake) == 5
    g.tick()  # grow 3 of 3
    assert len(g.snake) == 6


def test_star_disappears_after_20_turns():
    g = Game()
    g.star = (0, 0)
    g.star_timer = 1
    g.tick()
    assert g.star is None
    assert g.star_timer == 0


def test_speed_increases_every_10_points():
    g = Game()
    assert g.speed == 1
    g.score = 10
    assert g.speed == 2
    g.score = 25
    assert g.speed == 3


def test_no_tick_after_death():
    g = Game()
    g.alive = False
    g.snake = [(4, 3), (3, 3), (2, 3)]
    g.tick()
    assert g.snake[0] == (4, 3)  # didn't move


def test_maybe_spawn_star_respects_max_one():
    g = Game()
    g.star = (0, 0)
    g.star_timer = 10
    import random
    random.seed(0)  # ensure random would spawn if allowed
    g.maybe_spawn_star()
    assert g.star == (0, 0)  # unchanged


def test_apple_not_spawned_on_snake():
    g = Game()
    # Fill board almost completely with snake
    g.snake = [(x, y) for x in range(8) for y in range(8)]
    g.snake.pop()  # leave one free cell
    g.apple = None
    g._spawn_apple()
    assert g.apple is not None
    assert g.apple not in g.snake
