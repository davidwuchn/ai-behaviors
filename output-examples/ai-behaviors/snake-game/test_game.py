from random import Random
from game import (
    GameState, initial_state, tick, speed, level, is_valid_turn,
    enqueue_direction, resolve_direction, empty_cells, project_path, BOARD_SIZE,
)


def gs(**kw):
    defaults = dict(
        snake=((4, 4), (3, 4), (2, 4)), direction=(1, 0), apple=(0, 0),
        star=None, star_timer=0, score=0, phase="playing",
    )
    defaults.update(kw)
    return GameState(**defaults)


# --- initial state ---

def test_initial_state():
    s = initial_state(Random(42))
    assert s.snake == ((4, 4), (3, 4), (2, 4))
    assert s.direction == (1, 0)
    assert s.apple not in s.snake
    assert s.star is None
    assert s.score == 0
    assert s.phase == "start"


# --- speed ---

def test_speed():
    assert speed(0) == 3
    assert speed(9) == 3
    assert speed(10) == 4
    assert speed(50) == 8
    assert speed(100) == 8


# --- direction validation ---

def test_opposite_rejected():
    assert not is_valid_turn((1, 0), (-1, 0))
    assert not is_valid_turn((0, 1), (0, -1))


def test_valid_turns():
    assert is_valid_turn((1, 0), (0, 1))
    assert is_valid_turn((0, -1), (1, 0))
    assert is_valid_turn((1, 0), (1, 0))


# --- input queue ---

def test_enqueue_valid():
    q = []
    enqueue_direction(q, (0, 1), (1, 0))
    assert q == [(0, 1)]


def test_enqueue_opposite_rejected():
    q = []
    enqueue_direction(q, (-1, 0), (1, 0))
    assert q == []


def test_enqueue_validates_against_last_queued():
    q = []
    enqueue_direction(q, (0, 1), (1, 0))   # down vs right: ok
    enqueue_direction(q, (-1, 0), (1, 0))  # left vs last(down): ok
    assert q == [(0, 1), (-1, 0)]


def test_enqueue_rejects_opposite_of_last_queued():
    q = []
    enqueue_direction(q, (0, 1), (1, 0))
    enqueue_direction(q, (0, -1), (1, 0))  # up vs last(down): rejected
    assert q == [(0, 1)]


def test_resolve_pops():
    q = [(0, 1), (-1, 0)]
    assert resolve_direction(q, (1, 0)) == (0, 1)
    assert q == [(-1, 0)]


def test_resolve_empty():
    q = []
    assert resolve_direction(q, (1, 0)) == (1, 0)


# --- movement ---

def test_move_right():
    s = tick(gs(), Random(42))
    assert s.snake == ((5, 4), (4, 4), (3, 4))
    assert s.phase == "playing"


def test_move_down():
    s = tick(gs(direction=(0, 1)), Random(42))
    assert s.snake[0] == (4, 5)


# --- wall collision ---

def test_wall_right():
    assert tick(gs(snake=((7, 4), (6, 4), (5, 4))), Random(42)).phase == "lose"


def test_wall_left():
    assert tick(gs(snake=((0, 4), (1, 4), (2, 4)), direction=(-1, 0)), Random(42)).phase == "lose"


def test_wall_top():
    assert tick(gs(snake=((4, 0), (4, 1), (4, 2)), direction=(0, -1)), Random(42)).phase == "lose"


def test_wall_bottom():
    assert tick(gs(snake=((4, 7), (4, 6), (4, 5)), direction=(0, 1)), Random(42)).phase == "lose"


# --- self collision ---

def test_self_collision():
    snake = ((4, 3), (4, 4), (3, 4), (3, 3), (3, 2))
    assert tick(gs(snake=snake, direction=(-1, 0)), Random(42)).phase == "lose"


def test_tail_vacates_no_collision():
    snake = ((1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (2, 0))
    s = tick(gs(snake=snake, apple=(7, 7)), Random(42))
    assert s.phase == "playing"
    assert s.snake[0] == (2, 0)


def test_eating_at_tail_collides():
    snake = ((1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (2, 0))
    s = tick(gs(snake=snake, apple=(2, 0)), Random(42))
    assert s.phase == "lose"


# --- apple eating ---

def test_eat_apple_grows_and_scores():
    s = tick(gs(apple=(5, 4)), Random(42))
    assert len(s.snake) == 4
    assert s.snake[0] == (5, 4)
    assert s.score == 1


def test_eat_apple_spawns_new():
    s = tick(gs(apple=(5, 4)), Random(42))
    assert s.apple != (5, 4)
    assert s.apple not in s.snake


# --- star eating ---

def test_eat_star_no_growth():
    s = tick(gs(star=(5, 4), star_timer=10), Random(42))
    assert len(s.snake) == 3
    assert s.score == 5
    assert s.star is None
    assert s.star_timer == 0


# --- star timer ---

def test_star_timer_decrements():
    s = tick(gs(star=(6, 6), star_timer=10), Random(42))
    assert s.star == (6, 6)
    assert s.star_timer == 9


def test_star_disappears_at_zero():
    s = tick(gs(star=(6, 6), star_timer=1), Random(42))
    assert s.star is None
    assert s.star_timer == 0


# --- star spawning ---

def test_star_can_spawn_on_apple_eat():
    spawned = 0
    for seed in range(200):
        s = tick(gs(apple=(5, 4)), Random(seed))
        if s.star is not None:
            spawned += 1
            assert s.star not in s.snake
            assert s.star != s.apple
            assert s.star_timer == 20
    assert spawned > 0


def test_no_star_spawn_when_exists():
    for seed in range(50):
        s = tick(gs(apple=(5, 4), star=(6, 6), star_timer=15), Random(seed))
        if s.star is not None:
            assert s.star == (6, 6)


def test_no_star_without_apple():
    for seed in range(50):
        s = tick(gs(star=None), Random(seed))
        assert s.star is None


# --- win ---

def test_win_when_board_full():
    zigzag = []
    for y in range(8):
        row = list(range(8)) if y % 2 == 0 else list(reversed(range(8)))
        for x in row:
            zigzag.append((x, y))
    snake = tuple(reversed(zigzag[:63]))
    apple = zigzag[63]
    s = tick(gs(snake=snake, direction=(-1, 0), apple=apple, score=62), Random(42))
    assert s.phase == "win"
    assert len(s.snake) == 64
    assert s.score == 63


# --- empty_cells ---

def test_empty_cells():
    cells = empty_cells(((0, 0), (1, 0)), (2, 0))
    assert (0, 0) not in cells
    assert (1, 0) not in cells
    assert (2, 0) not in cells
    assert len(cells) == 64 - 3


# --- level ---

def test_level():
    assert level(0) == 1
    assert level(9) == 1
    assert level(10) == 2
    assert level(50) == 6
    assert level(100) == 6


# --- project_path ---

def test_project_empty_queue():
    assert project_path((4, 4), []) == []


def test_project_one_move():
    assert project_path((4, 4), [(0, -1)]) == [(4, 3)]


def test_project_chain():
    path = project_path((4, 4), [(0, 1), (-1, 0), (0, -1)])
    assert path == [(4, 5), (3, 5), (3, 4)]


# --- death cause ---

def test_wall_death():
    s = tick(gs(snake=((7, 4), (6, 4), (5, 4))), Random(42))
    assert s.death == "wall"


def test_self_death():
    snake = ((4, 3), (4, 4), (3, 4), (3, 3), (3, 2))
    s = tick(gs(snake=snake, direction=(-1, 0)), Random(42))
    assert s.death == "self"


def test_no_death_on_move():
    assert tick(gs(), Random(42)).death is None


def test_no_death_on_apple():
    assert tick(gs(apple=(5, 4)), Random(42)).death is None
