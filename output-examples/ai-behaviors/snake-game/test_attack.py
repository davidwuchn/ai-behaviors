"""Attack tests. Prove the code guilty."""
from random import Random
from dataclasses import replace
from game import (
    GameState, initial_state, tick, speed, is_valid_turn,
    enqueue_direction, resolve_direction, empty_cells, spawn_food,
    BOARD_SIZE, UP, DOWN, LEFT, RIGHT,
)


def gs(**kw):
    defaults = dict(
        snake=((4, 4), (3, 4), (2, 4)), direction=(1, 0), apple=(0, 0),
        star=None, star_timer=0, score=0, phase="playing",
    )
    defaults.update(kw)
    return GameState(**defaults)


# ====== FIX VERIFIED: tick() guards on phase ======

def test_tick_on_lose_stays_lose():
    state = gs(phase="lose")
    s = tick(state, Random(42))
    assert s.phase == "lose"
    assert s.snake == state.snake


def test_tick_on_start_stays_start():
    state = gs(phase="start")
    s = tick(state, Random(42))
    assert s.phase == "start"


def test_tick_on_win_stays_win():
    state = gs(phase="win")
    s = tick(state, Random(42))
    assert s.phase == "win"


# ====== Missing test coverage: star timer during apple-eat tick ======

def test_star_timer_decrements_when_apple_eaten():
    """Pre-existing star should still tick down on the turn you eat an apple."""
    state = gs(apple=(5, 4), star=(6, 6), star_timer=5)
    s = tick(state, Random(42))
    assert s.star == (6, 6)
    assert s.star_timer == 4


def test_star_expires_on_apple_eat_tick():
    """Star at timer=1 should vanish even if apple is also eaten this tick."""
    state = gs(apple=(5, 4), star=(6, 6), star_timer=1)
    s = tick(state, Random(42))
    assert s.star is None
    assert s.star_timer == 0
    assert s.score == 1  # apple only


# ====== Sequence: multi-tick queue drain ======

def test_queue_drains_correctly_over_two_ticks():
    state = gs()
    queue = []
    enqueue_direction(queue, UP, state.direction)       # up vs right: ok
    enqueue_direction(queue, LEFT, state.direction)      # left vs up: ok
    assert len(queue) == 2

    positions = []
    for _ in range(2):
        d = resolve_direction(queue, state.direction)
        state = replace(state, direction=d)
        state = tick(state, Random(42))
        positions.append(state.snake[0])

    assert positions == [(4, 3), (3, 3)]
    assert queue == []


def test_direction_persists_after_queue_empty():
    """Once queue empties, snake keeps its last resolved direction."""
    state = gs()
    queue = []
    enqueue_direction(queue, UP, state.direction)

    d = resolve_direction(queue, state.direction)
    state = replace(state, direction=d)
    state = tick(state, Random(42))  # moves up

    # Queue now empty — should keep moving up
    d = resolve_direction(queue, state.direction)
    state = replace(state, direction=d)
    state = tick(state, Random(42))

    assert state.snake[0] == (4, 2)  # two steps up from (4,4)


# ====== Boundary: score at speed transition ======

def test_speed_transition_at_boundary():
    """Eating apple at score 9→10 should change speed from 3 to 4."""
    state = gs(apple=(5, 4), score=9)
    s = tick(state, Random(42))
    assert s.score == 10
    assert speed(s.score) == 4
    assert speed(9) == 3


# ====== Boundary: repeated apples fill the board ======

def test_consecutive_growth():
    """Chain three apple eats and verify length accumulates."""
    state = gs(apple=(5, 4))
    state = tick(state, Random(42))
    assert len(state.snake) == 4

    # Force star=None to avoid accidental apple+star overlap
    state = replace(state, apple=(6, 4), star=None, star_timer=0)
    state = tick(state, Random(42))
    assert len(state.snake) == 5

    state = replace(state, apple=(7, 4), star=None, star_timer=0)
    state = tick(state, Random(42))
    assert len(state.snake) == 6
    assert state.score == 3


# ====== BUG: tick allows eating apple AND star at same cell ======

def test_apple_star_same_cell_both_eaten():
    """If apple and star share a cell (impossible state), both fire.
    tick() doesn't guard against this invariant violation."""
    state = gs(apple=(5, 4), star=(5, 4), star_timer=10)
    s = tick(state, Random(42))
    # Both ate_apple and ate_star become True
    assert s.score == 6  # 1 (apple) + 5 (star)
    assert len(s.snake) == 4  # grew from apple
    # The star block clears star AFTER apple block may have spawned a new one
    assert s.star is None  # ate_star clears it, even if apple block spawned one


# ====== Negative space: star spawn probability is roughly 25% ======

def test_star_spawn_rate_roughly_25_percent():
    """Statistical check: star spawn rate ~25% across many seeds."""
    spawned = sum(
        1 for seed in range(1000)
        if tick(gs(apple=(5, 4)), Random(seed)).star is not None
    )
    # 25% of 1000 = 250. Allow wide margin for randomness.
    assert 150 < spawned < 350, f"star spawn rate {spawned}/1000 outside expected range"


# ====== Negative space: star never on snake or apple ======

def test_star_position_invariant():
    """Across many seeds, spawned star is never on snake or apple."""
    for seed in range(500):
        s = tick(gs(apple=(5, 4)), Random(seed))
        if s.star is not None:
            assert s.star not in s.snake
            assert s.star != s.apple


# ====== Negative space: new apple never on snake or star ======

def test_apple_position_invariant():
    """After eating, new apple never overlaps snake or star."""
    for seed in range(500):
        s = tick(gs(apple=(5, 4)), Random(seed))
        assert s.apple not in s.snake
        if s.star is not None:
            assert s.apple != s.star


# ====== Edge: (0,0) direction via API ======

def test_zero_direction_causes_self_collision():
    """A (0,0) direction means head stays in place — self collision."""
    state = gs(direction=(0, 0))
    s = tick(state, Random(42))
    # new_head = (4,4) = current head. body sans tail = snake[:-1] = ((4,4),(3,4))
    # (4,4) in ((4,4),(3,4)) → True → lose
    assert s.phase == "lose"


# ====== Edge: wall collision preserves state (no mutation) ======

def test_wall_lose_preserves_snake():
    """On wall collision, snake position should NOT advance."""
    state = gs(snake=((7, 4), (6, 4), (5, 4)), direction=(1, 0))
    s = tick(state, Random(42))
    assert s.phase == "lose"
    assert s.snake == ((7, 4), (6, 4), (5, 4))  # unchanged


def test_self_collision_preserves_snake():
    """On self collision, snake position should NOT advance."""
    snake = ((4, 3), (4, 4), (3, 4), (3, 3), (3, 2))
    state = gs(snake=snake, direction=(-1, 0))
    s = tick(state, Random(42))
    assert s.phase == "lose"
    assert s.snake == snake  # unchanged


# ====== Edge: star eat on timer=1 (eat beats expiry) ======

def test_star_eaten_at_timer_one():
    """Eating star on its last turn should still award points."""
    state = gs(star=(5, 4), star_timer=1)
    s = tick(state, Random(42))
    assert s.score == 5
    assert s.star is None


# ====== Edge: empty_cells with full board ======

def test_empty_cells_full_board():
    all_cells = tuple((x, y) for x in range(8) for y in range(8))
    assert empty_cells(all_cells, None) == []


def test_spawn_food_full_board():
    all_cells = tuple((x, y) for x in range(8) for y in range(8))
    assert spawn_food(all_cells, None, Random(42)) is None


# ====== FIX VERIFIED: queue limits ======

def test_enqueue_same_direction_dropped():
    """Pressing same direction as current is silently dropped."""
    q = []
    enqueue_direction(q, RIGHT, RIGHT)
    assert len(q) == 0


def test_enqueue_capped_at_three():
    """Queue rejects entries beyond size 3."""
    q = []
    enqueue_direction(q, UP, RIGHT)
    enqueue_direction(q, LEFT, RIGHT)
    enqueue_direction(q, DOWN, RIGHT)
    assert len(q) == 3
    enqueue_direction(q, RIGHT, RIGHT)  # rejected: queue full
    assert len(q) == 3
