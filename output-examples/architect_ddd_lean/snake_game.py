"""Snake game — 8x8 board, pygame."""

import random
from collections import deque
from enum import Enum

import pygame

# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


OPPOSITES = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

BOARD_SIZE = 8


def random_free_cell(occupied: set[tuple[int, int]]) -> tuple[int, int]:
    free = [
        (x, y)
        for x in range(BOARD_SIZE)
        for y in range(BOARD_SIZE)
        if (x, y) not in occupied
    ]
    return random.choice(free) if free else (-1, -1)


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    GAME_OVER = "game_over"


class Game:
    """Aggregate root — all game state and rules live here."""

    def __init__(self) -> None:
        self.state = GameState.WAITING
        self._reset()

    def _reset(self) -> None:
        mid = BOARD_SIZE // 2
        self.snake: list[tuple[int, int]] = [
            (mid, mid), (mid - 1, mid), (mid - 2, mid)
        ]
        self.direction = Direction.RIGHT
        self.input_queue: deque[Direction] = deque()
        self.grow_pending = 0
        self.score = 0
        self.speed_level = 1
        self.turn = 0
        self.apple: tuple[int, int] = (-1, -1)
        self.star: tuple[int, int] | None = None
        self.star_turns_left = 0
        self._place_apple()

    def _occupied(self) -> set[tuple[int, int]]:
        cells = set(self.snake)
        if self.apple != (-1, -1):
            cells.add(self.apple)
        if self.star is not None:
            cells.add(self.star)
        return cells

    def _place_apple(self) -> None:
        self.apple = random_free_cell(self._occupied())

    def _maybe_spawn_star(self) -> None:
        if self.star is not None:
            return
        if random.random() < 0.08:
            occupied = self._occupied()
            cell = random_free_cell(occupied)
            if cell != (-1, -1):
                self.star = cell
                self.star_turns_left = 20

    def start(self) -> None:
        self._reset()
        self.state = GameState.PLAYING

    def enqueue_direction(self, d: Direction) -> None:
        # Validate against the effective current direction (last queued or actual).
        reference = self.input_queue[-1] if self.input_queue else self.direction
        if d != reference and d != OPPOSITES[reference]:
            self.input_queue.append(d)

    def tick(self) -> None:
        if self.state != GameState.PLAYING:
            return

        # Consume next queued direction.
        if self.input_queue:
            self.direction = self.input_queue.popleft()

        self.turn += 1

        # Move head.
        hx, hy = self.snake[0]
        dx, dy = self.direction.value
        new_head = (hx + dx, hy + dy)

        # Wall collision.
        nx, ny = new_head
        if nx < 0 or nx >= BOARD_SIZE or ny < 0 or ny >= BOARD_SIZE:
            self.state = GameState.GAME_OVER
            return

        # Self collision.
        if new_head in self.snake:
            self.state = GameState.GAME_OVER
            return

        self.snake.insert(0, new_head)

        # Apple.
        if new_head == self.apple:
            self.score += 1
            self.grow_pending += 1
            self._place_apple()

        # Star.
        if self.star is not None and new_head == self.star:
            self.score += 3
            self.grow_pending += 3
            self.star = None
            self.star_turns_left = 0

        # Tail.
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.snake.pop()

        # Star timer.
        if self.star is not None:
            self.star_turns_left -= 1
            if self.star_turns_left <= 0:
                self.star = None

        self._maybe_spawn_star()

        # Speed.
        self.speed_level = 1 + self.score // 10

    @property
    def tick_interval_ms(self) -> int:
        return max(80, 400 - (self.speed_level - 1) * 40)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

CELL_PX = 64
BOARD_PX = CELL_PX * BOARD_SIZE
HUD_HEIGHT = 48
WINDOW_W = BOARD_PX
WINDOW_H = BOARD_PX + HUD_HEIGHT

COLOR_BG = (20, 20, 20)
COLOR_GRID = (40, 40, 40)
COLOR_SNAKE = (0, 200, 80)
COLOR_SNAKE_HEAD = (0, 255, 100)
COLOR_APPLE = (220, 40, 40)
COLOR_STAR = (255, 215, 0)
COLOR_HUD_BG = (30, 30, 30)
COLOR_TEXT = (220, 220, 220)

KEY_MAP = {
    pygame.K_w: Direction.UP,
    pygame.K_a: Direction.LEFT,
    pygame.K_s: Direction.DOWN,
    pygame.K_d: Direction.RIGHT,
    pygame.K_UP: Direction.UP,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_RIGHT: Direction.RIGHT,
}


def draw(surface: pygame.Surface, game: Game, font: pygame.font.Font) -> None:
    surface.fill(COLOR_BG)

    # Grid lines.
    for i in range(1, BOARD_SIZE):
        x = i * CELL_PX
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, BOARD_PX))
        pygame.draw.line(surface, COLOR_GRID, (0, x), (BOARD_PX, x))

    # Apple.
    _draw_cell(surface, game.apple, COLOR_APPLE)

    # Star.
    if game.star is not None:
        _draw_star(surface, game.star)

    # Snake.
    for i, seg in enumerate(game.snake):
        color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE
        _draw_cell(surface, seg, color)

    # HUD.
    hud_rect = pygame.Rect(0, BOARD_PX, WINDOW_W, HUD_HEIGHT)
    pygame.draw.rect(surface, COLOR_HUD_BG, hud_rect)
    hud_text = f"Score: {game.score}   Speed: {game.speed_level}"
    text_surf = font.render(hud_text, True, COLOR_TEXT)
    surface.blit(text_surf, (12, BOARD_PX + 12))

    # Overlay messages.
    if game.state == GameState.WAITING:
        _draw_overlay(surface, font, "Press ENTER to start")
    elif game.state == GameState.GAME_OVER:
        _draw_overlay(surface, font, f"Game Over — Score: {game.score}", "Press ENTER to restart")


def _draw_cell(surface: pygame.Surface, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
    x, y = pos
    margin = 2
    rect = pygame.Rect(x * CELL_PX + margin, y * CELL_PX + margin, CELL_PX - 2 * margin, CELL_PX - 2 * margin)
    pygame.draw.rect(surface, color, rect, border_radius=6)


def _draw_star(surface: pygame.Surface, pos: tuple[int, int]) -> None:
    cx = pos[0] * CELL_PX + CELL_PX // 2
    cy = pos[1] * CELL_PX + CELL_PX // 2
    r_outer = CELL_PX // 2 - 4
    r_inner = r_outer // 2
    import math
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    pygame.draw.polygon(surface, COLOR_STAR, points)


def _draw_overlay(surface: pygame.Surface, font: pygame.font.Font, *lines: str) -> None:
    overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (0, 0))
    total_h = len(lines) * 36
    start_y = (BOARD_PX - total_h) // 2
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, COLOR_TEXT)
        rect = text_surf.get_rect(center=(WINDOW_W // 2, start_y + i * 36))
        surface.blit(text_surf, rect)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Snake")
    font = pygame.font.SysFont("monospace", 22)
    clock = pygame.time.Clock()

    game = Game()

    TICK_EVENT = pygame.USEREVENT + 1
    timer_running = False

    def start_timer() -> None:
        nonlocal timer_running
        pygame.time.set_timer(TICK_EVENT, game.tick_interval_ms)
        timer_running = True

    def stop_timer() -> None:
        nonlocal timer_running
        pygame.time.set_timer(TICK_EVENT, 0)
        timer_running = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if game.state in (GameState.WAITING, GameState.GAME_OVER):
                        game.start()
                        start_timer()
                elif event.key in KEY_MAP and game.state == GameState.PLAYING:
                    game.enqueue_direction(KEY_MAP[event.key])

            elif event.type == TICK_EVENT:
                game.tick()
                # Update timer speed if it changed.
                pygame.time.set_timer(TICK_EVENT, game.tick_interval_ms)
                if game.state == GameState.GAME_OVER:
                    stop_timer()

        draw(screen, game, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
