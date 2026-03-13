from dataclasses import dataclass, replace
from random import Random
from typing import Optional

BOARD_SIZE = 8

Cell = tuple[int, int]
Direction = tuple[int, int]

RIGHT: Direction = (1, 0)
LEFT: Direction = (-1, 0)
UP: Direction = (0, -1)
DOWN: Direction = (0, 1)


@dataclass(frozen=True)
class GameState:
    snake: tuple[Cell, ...]
    direction: Direction
    apple: Cell
    star: Optional[Cell]
    star_timer: int
    score: int
    phase: str
    death: Optional[str] = None


def speed(score: int) -> int:
    return min(3 + score // 10, 8)


def level(score: int) -> int:
    return min(1 + score // 10, 6)


def is_valid_turn(current: Direction, proposed: Direction) -> bool:
    return (current[0] + proposed[0], current[1] + proposed[1]) != (0, 0)


MAX_QUEUE = 3


def enqueue_direction(queue: list, new_dir: Direction, current_dir: Direction) -> None:
    if len(queue) >= MAX_QUEUE:
        return
    effective = queue[-1] if queue else current_dir
    if new_dir == effective:
        return
    if is_valid_turn(effective, new_dir):
        queue.append(new_dir)


def resolve_direction(queue: list, current_dir: Direction) -> Direction:
    return queue.pop(0) if queue else current_dir


def project_path(head: Cell, queue: list) -> list[Cell]:
    cells = []
    x, y = head
    for dx, dy in queue:
        x, y = x + dx, y + dy
        cells.append((x, y))
    return cells


def empty_cells(snake: tuple, exclude: Optional[Cell]) -> list[Cell]:
    occupied = set(snake)
    if exclude is not None:
        occupied.add(exclude)
    return [
        (x, y)
        for x in range(BOARD_SIZE)
        for y in range(BOARD_SIZE)
        if (x, y) not in occupied
    ]


def spawn_food(snake: tuple, exclude: Optional[Cell], rng: Random) -> Optional[Cell]:
    cells = empty_cells(snake, exclude)
    return rng.choice(cells) if cells else None


def initial_state(rng: Random) -> GameState:
    snake = ((4, 4), (3, 4), (2, 4))
    apple = spawn_food(snake, None, rng)
    return GameState(snake, RIGHT, apple, None, 0, 0, "start")


def tick(state: GameState, rng: Random) -> GameState:
    if state.phase != "playing":
        return state

    hx, hy = state.snake[0]
    dx, dy = state.direction
    new_head = (hx + dx, hy + dy)

    if not (0 <= new_head[0] < BOARD_SIZE and 0 <= new_head[1] < BOARD_SIZE):
        return replace(state, phase="lose", death="wall")

    ate_apple = new_head == state.apple
    ate_star = state.star is not None and new_head == state.star

    new_body = state.snake if ate_apple else state.snake[:-1]

    if new_head in new_body:
        return replace(state, phase="lose", death="self")

    new_snake = (new_head,) + new_body
    score = state.score
    apple = state.apple
    star = state.star
    star_timer = state.star_timer
    star_spawned = False

    if ate_apple:
        score += 1
        if len(new_snake) == BOARD_SIZE * BOARD_SIZE:
            return GameState(new_snake, state.direction, apple, None, 0, score, "win")
        apple = spawn_food(new_snake, star, rng)
        if apple is None and star is not None:
            star = None
            star_timer = 0
            apple = spawn_food(new_snake, None, rng)
        if star is None:
            if rng.random() < 0.25:
                cell = spawn_food(new_snake, apple, rng)
                if cell is not None:
                    star = cell
                    star_timer = 20
                    star_spawned = True

    if ate_star:
        score += 5
        star = None
        star_timer = 0

    if star is not None and not star_spawned:
        star_timer -= 1
        if star_timer <= 0:
            star = None
            star_timer = 0

    return GameState(new_snake, state.direction, apple, star, star_timer, score, "playing")
