#!/usr/bin/env python3
"""Snake game on an 8x8 grid."""

import math
import random
import sys
from collections import deque

import pygame

# Grid
GRID = 8
CELL = 80
HDR = 50
W = GRID * CELL
H = GRID * CELL + HDR

# Colors (dark theme)
C_BG = (30, 30, 46)
C_GRID = (50, 50, 66)
C_SNAKE = (64, 200, 100)
C_HEAD = (100, 255, 130)
C_APPLE = (230, 69, 83)
C_STAR = (249, 226, 175)
C_TEXT = (205, 214, 244)
C_HDR = (24, 24, 37)
C_OVERLAY = (0, 0, 0, 160)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# Tuning
BASE_SPEED = 4
SPEED_INC = 1
MAX_SPEED = 15
STAR_CHANCE = 0.08
STAR_LIFE = 20

# States
WAITING, PLAYING, GAME_OVER, WON = range(4)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 32, bold=True)
        self.state = WAITING
        self._reset()

    def _reset(self):
        self.snake = [(2, 4), (3, 4), (4, 4)]
        self.direction = RIGHT
        self.queue = deque()
        self.score = 0
        self.apple = None
        self.star = None
        self.star_ttl = 0
        self.grow = 0
        self._place_apple()

    def _free_cells(self, exclude=None):
        occ = set(self.snake)
        if exclude:
            occ.update(exclude)
        return [(x, y) for x in range(GRID) for y in range(GRID) if (x, y) not in occ]

    def _place_apple(self):
        extra = [self.star] if self.star else []
        free = self._free_cells(extra)
        self.apple = random.choice(free) if free else None

    def _place_star(self):
        extra = [self.apple] if self.apple else []
        free = self._free_cells(extra)
        if free:
            self.star = random.choice(free)
            self.star_ttl = STAR_LIFE

    def speed(self):
        return min(BASE_SPEED + (self.score // 10) * SPEED_INC, MAX_SPEED)

    def _enqueue(self, key):
        dirs = {
            pygame.K_w: UP, pygame.K_UP: UP,
            pygame.K_s: DOWN, pygame.K_DOWN: DOWN,
            pygame.K_a: LEFT, pygame.K_LEFT: LEFT,
            pygame.K_d: RIGHT, pygame.K_RIGHT: RIGHT,
        }
        d = dirs.get(key)
        if not d:
            return
        last = self.queue[-1] if self.queue else self.direction
        if d != OPPOSITE[last] and d != last:
            self.queue.append(d)

    def _tick(self):
        # Consume queued direction
        if self.queue:
            nxt = self.queue.popleft()
            if nxt != OPPOSITE[self.direction]:
                self.direction = nxt

        hx, hy = self.snake[-1]
        nx, ny = hx + self.direction[0], hy + self.direction[1]

        # Wall collision
        if not (0 <= nx < GRID and 0 <= ny < GRID):
            self.state = GAME_OVER
            return

        # Self collision (tail will move away if not growing)
        body = set(self.snake)
        if self.grow == 0:
            body.discard(self.snake[0])
        if (nx, ny) in body:
            self.state = GAME_OVER
            return

        self.snake.append((nx, ny))

        # Apple
        if self.apple and (nx, ny) == self.apple:
            self.score += 1
            self.grow += 1
            self._place_apple()
            if not self.apple:
                self.state = WON
                return

        # Star
        if self.star and (nx, ny) == self.star:
            self.score += 3
            self.grow += 3
            self.star = None
            self.star_ttl = 0

        # Tail
        if self.grow > 0:
            self.grow -= 1
        else:
            self.snake.pop(0)

        # Star lifecycle
        if self.star:
            self.star_ttl -= 1
            if self.star_ttl <= 0:
                self.star = None
        elif random.random() < STAR_CHANCE:
            self._place_star()

    # -- Drawing ---------------------------------------------------------------

    def _draw(self):
        self.screen.fill(C_BG)

        # Header
        pygame.draw.rect(self.screen, C_HDR, (0, 0, W, HDR))
        self.screen.blit(
            self.font.render(f"Score: {self.score}", True, C_TEXT), (10, 13)
        )
        st = self.font.render(f"Speed: {self.speed()}", True, C_TEXT)
        self.screen.blit(st, (W - st.get_width() - 10, 13))

        # Grid lines
        for i in range(GRID + 1):
            pygame.draw.line(self.screen, C_GRID, (i * CELL, HDR), (i * CELL, H))
            pygame.draw.line(self.screen, C_GRID, (0, i * CELL + HDR), (W, i * CELL + HDR))

        # Apple
        if self.apple:
            ax, ay = self.apple
            r = pygame.Rect(ax * CELL + 6, ay * CELL + HDR + 6, CELL - 12, CELL - 12)
            pygame.draw.ellipse(self.screen, C_APPLE, r)

        # Star (blinks when < 5 turns remain)
        if self.star:
            if self.star_ttl > 5 or pygame.time.get_ticks() % 400 < 200:
                self._draw_star_shape(self.star)

        # Snake
        for i, (sx, sy) in enumerate(self.snake):
            c = C_HEAD if i == len(self.snake) - 1 else C_SNAKE
            r = pygame.Rect(sx * CELL + 2, sy * CELL + HDR + 2, CELL - 4, CELL - 4)
            pygame.draw.rect(self.screen, c, r, border_radius=10)

        # Overlays
        if self.state == WAITING:
            self._overlay("SNAKE", "Press ENTER to start")
        elif self.state == GAME_OVER:
            self._overlay("GAME OVER", f"Score: {self.score}  |  ENTER to restart")
        elif self.state == WON:
            self._overlay("YOU WIN!", f"Score: {self.score}  |  ENTER to restart")

        pygame.display.flip()

    def _draw_star_shape(self, pos):
        cx = pos[0] * CELL + CELL // 2
        cy = pos[1] * CELL + HDR + CELL // 2
        pts = []
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            r = (CELL // 2 - 6) if i % 2 == 0 else (CELL // 5)
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        pygame.draw.polygon(self.screen, C_STAR, pts)

    def _overlay(self, title, sub):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill(C_OVERLAY)
        self.screen.blit(s, (0, 0))
        t = self.big_font.render(title, True, C_TEXT)
        u = self.font.render(sub, True, C_TEXT)
        self.screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 30))
        self.screen.blit(u, (W // 2 - u.get_width() // 2, H // 2 + 20))

    # -- Main loop -------------------------------------------------------------

    def run(self):
        timer = 0.0
        while True:
            dt = self.clock.tick(60) / 1000.0

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if self.state == WAITING and ev.key == pygame.K_RETURN:
                        self.state = PLAYING
                    elif self.state in (GAME_OVER, WON) and ev.key == pygame.K_RETURN:
                        self._reset()
                        self.state = PLAYING
                    elif self.state == PLAYING:
                        self._enqueue(ev.key)

            if self.state == PLAYING:
                timer += dt
                interval = 1.0 / self.speed()
                while timer >= interval and self.state == PLAYING:
                    timer -= interval
                    self._tick()
            else:
                timer = 0.0

            self._draw()


if __name__ == "__main__":
    Game().run()
