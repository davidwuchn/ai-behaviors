#!/usr/bin/env python3
import random
import sys

import pygame

# --- Constants ---
GRID_SIZE = 8
CELL_SIZE = 64
HEADER_HEIGHT = 48
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + HEADER_HEIGHT

BASE_TICK_RATE = 5
TICK_INCREMENT = 1
MAX_TICK_RATE = 15
POINTS_PER_SPEED = 10

STAR_SPAWN_CHANCE = 0.05
STAR_LIFETIME = 20
STAR_GROWTH = 3

CELL_INSET = 2
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)
HEAD_GREEN = (80, 220, 80)
BODY_GREEN = (40, 160, 40)
RED = (220, 50, 50)
GOLD = (255, 215, 0)
OVERLAY_COLOR = (0, 0, 0, 180)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

KEY_MAP = {
    pygame.K_w: UP, pygame.K_UP: UP,
    pygame.K_s: DOWN, pygame.K_DOWN: DOWN,
    pygame.K_a: LEFT, pygame.K_LEFT: LEFT,
    pygame.K_d: RIGHT, pygame.K_RIGHT: RIGHT,
}


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(4, 4), (3, 4), (2, 4)]
        self.direction = RIGHT
        self.input_queue = []
        self.score = 0
        self.speed = 1
        self.alive = True
        self.grow_pending = 0
        self.apple = None
        self.star = None
        self.star_timer = 0
        self._spawn_apple()

    def _free_cells(self):
        occupied = set(self.snake)
        if self.apple:
            occupied.add(self.apple)
        if self.star:
            occupied.add(self.star)
        return [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
                if (x, y) not in occupied]

    def _spawn_apple(self):
        free = self._free_cells()
        self.apple = random.choice(free) if free else None

    def _maybe_spawn_star(self):
        if self.star is not None:
            return
        if random.random() < STAR_SPAWN_CHANCE:
            free = self._free_cells()
            if free:
                self.star = random.choice(free)
                self.star_timer = STAR_LIFETIME

    def queue_direction(self, direction):
        ref = self.input_queue[-1] if self.input_queue else self.direction
        if direction != OPPOSITES.get(ref) and direction != ref:
            self.input_queue.append(direction)

    def _process_input_queue(self):
        while self.input_queue:
            d = self.input_queue.pop(0)
            if d != OPPOSITES.get(self.direction):
                self.direction = d
                return

    def tick(self):
        if not self.alive:
            return

        self._process_input_queue()

        hx, hy = self.snake[0]
        dx, dy = self.direction
        nx, ny = hx + dx, hy + dy

        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            self.alive = False
            return

        if self.grow_pending > 0:
            collision_body = self.snake
        else:
            collision_body = self.snake[:-1]

        if (nx, ny) in collision_body:
            self.alive = False
            return

        self.snake.insert(0, (nx, ny))

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.snake.pop()

        if (nx, ny) == self.apple:
            self.score += 1
            self.grow_pending += 1
            self._spawn_apple()

        if self.star and (nx, ny) == self.star:
            self.score += 3
            self.grow_pending += STAR_GROWTH
            self.star = None
            self.star_timer = 0

        if self.star is not None:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star = None

        self._maybe_spawn_star()
        self._update_speed()

    def _update_speed(self):
        self.speed = 1 + self.score // POINTS_PER_SPEED

    def get_tick_rate(self):
        return min(BASE_TICK_RATE + (self.speed - 1) * TICK_INCREMENT, MAX_TICK_RATE)


def draw_rounded_rect(surface, color, rect, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_star_polygon(surface, center, size):
    import math
    cx, cy = center
    points = []
    for i in range(16):
        angle = math.pi * 2 * i / 16 - math.pi / 2
        r = size if i % 2 == 0 else size * 0.5
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    pygame.draw.polygon(surface, GOLD, points)


def render(screen, game, font, state):
    screen.fill(DARK_GRAY)

    # Header
    score_text = font.render(f"Score: {game.score}", True, WHITE)
    speed_text = font.render(f"Speed: {game.speed}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(speed_text, (WINDOW_WIDTH - speed_text.get_width() - 10, 10))

    # Grid area offset
    oy = HEADER_HEIGHT

    # Apple
    if game.apple:
        ax, ay = game.apple
        cx = ax * CELL_SIZE + CELL_SIZE // 2
        cy = ay * CELL_SIZE + CELL_SIZE // 2 + oy
        pygame.draw.circle(screen, RED, (cx, cy), CELL_SIZE // 2 - CELL_INSET - 4)

    # Star
    if game.star:
        sx, sy = game.star
        cx = sx * CELL_SIZE + CELL_SIZE // 2
        cy = sy * CELL_SIZE + CELL_SIZE // 2 + oy
        draw_star_polygon(screen, (cx, cy), CELL_SIZE // 2 - CELL_INSET - 2)

    # Snake
    for i, (x, y) in enumerate(game.snake):
        color = HEAD_GREEN if i == 0 else BODY_GREEN
        rect = pygame.Rect(
            x * CELL_SIZE + CELL_INSET,
            y * CELL_SIZE + CELL_INSET + oy,
            CELL_SIZE - 2 * CELL_INSET,
            CELL_SIZE - 2 * CELL_INSET,
        )
        draw_rounded_rect(screen, color, rect)

    # Overlays
    if state != "playing":
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        if state == "start_screen":
            title = font.render("SNAKE", True, HEAD_GREEN)
            subtitle = font.render("Press ENTER to start", True, WHITE)
        else:
            title = font.render("GAME OVER", True, RED)
            subtitle = font.render(f"Score: {game.score}  -  Press ENTER", True, WHITE)

        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2,
                            WINDOW_HEIGHT // 2 - 40))
        screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2,
                                WINDOW_HEIGHT // 2 + 10))

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 24, bold=True)

    game = Game()
    state = "start_screen"
    tick_accumulator = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if state == "start_screen":
                        state = "playing"
                    elif state == "game_over":
                        game.reset()
                        state = "playing"
                elif state == "playing" and event.key in KEY_MAP:
                    game.queue_direction(KEY_MAP[event.key])

        if state == "playing" and game.alive:
            tick_interval = 1.0 / game.get_tick_rate()
            tick_accumulator += dt
            while tick_accumulator >= tick_interval:
                tick_accumulator -= tick_interval
                game.tick()
                if not game.alive:
                    state = "game_over"
                    tick_accumulator = 0.0
                    break

        render(screen, game, font, state)


if __name__ == "__main__":
    main()
