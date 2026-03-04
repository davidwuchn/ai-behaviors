import random
from collections import deque
from enum import Enum

OPPOSITES = {
    (0, -1): (0, 1),
    (0, 1): (0, -1),
    (-1, 0): (1, 0),
    (1, 0): (-1, 0),
}


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Game:
    BOARD_SIZE = 8

    def __init__(self):
        mid = self.BOARD_SIZE // 2
        self.snake = [(mid, mid - 1), (mid - 1, mid - 1), (mid - 2, mid - 1)]
        self.direction = Direction.RIGHT
        self._dir_queue = deque()
        self.apple = None
        self.star = None
        self.star_timer = 0
        self.score = 0
        self.alive = True
        self._grow = 0
        self._spawn_apple()

    @property
    def speed(self):
        return 1 + self.score // 10

    def queue_direction(self, d):
        last = self._dir_queue[-1] if self._dir_queue else self.direction
        if d.value != OPPOSITES[last.value] and d != last:
            self._dir_queue.append(d)

    def tick(self):
        if not self.alive:
            return
        if self._dir_queue:
            self.direction = self._dir_queue.popleft()
        dx, dy = self.direction.value
        head = self.snake[0]
        new_head = (head[0] + dx, head[1] + dy)

        # Wall collision
        if not (0 <= new_head[0] < self.BOARD_SIZE and 0 <= new_head[1] < self.BOARD_SIZE):
            self.alive = False
            return

        # Self collision
        if new_head in self.snake:
            self.alive = False
            return

        self.snake.insert(0, new_head)

        # Apple
        if new_head == self.apple:
            self._grow += 1
            self.score += 1
            self._spawn_apple()

        # Star
        if new_head == self.star:
            self._grow += 3
            self.score += 3
            self.star = None
            self.star_timer = 0

        # Grow or move
        if self._grow > 0:
            self._grow -= 1
        else:
            self.snake.pop()

        # Star timer
        if self.star is not None:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star = None
                self.star_timer = 0

    def _free_cells(self):
        occupied = set(self.snake)
        if self.apple:
            occupied.add(self.apple)
        if self.star:
            occupied.add(self.star)
        return [(x, y) for x in range(self.BOARD_SIZE) for y in range(self.BOARD_SIZE)
                if (x, y) not in occupied]

    def _spawn_apple(self):
        free = self._free_cells()
        if free:
            self.apple = random.choice(free)

    def maybe_spawn_star(self):
        if self.star is None and random.random() < 0.1:
            free = self._free_cells()
            if free:
                self.star = random.choice(free)
                self.star_timer = 20
