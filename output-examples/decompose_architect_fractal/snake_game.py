#!/usr/bin/env python3
"""Snake game — 8x8 grid, pygame."""

import math
import random
import sys
from collections import deque
from enum import Enum, auto

import pygame

# ── Constants ──────────────────────────────────────────────

GRID = 8
CELL = 80
PAD = 2
BOARD = GRID * CELL
HUD_H = 60
WIN_SIZE = (BOARD, BOARD + HUD_H)
FPS = 60

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
KEYS = {
    pygame.K_w: UP, pygame.K_UP: UP,
    pygame.K_s: DOWN, pygame.K_DOWN: DOWN,
    pygame.K_a: LEFT, pygame.K_LEFT: LEFT,
    pygame.K_d: RIGHT, pygame.K_RIGHT: RIGHT,
}

BASE_TPS = 3
TPS_PER_LEVEL = 1
STAR_CHANCE = 0.10
STAR_LIFE = 20

BG = (15, 15, 15)
GRID_CLR = (30, 30, 30)
HEAD_CLR = (0, 200, 0)
BODY_CLR = (0, 155, 0)
APPLE_CLR = (220, 30, 30)
STAR_CLR = (255, 215, 0)
TEXT_CLR = (220, 220, 220)
OVERLAY_BG = (0, 0, 0, 180)


# ── Phase ──────────────────────────────────────────────────

class Phase(Enum):
    WAITING = auto()
    PLAYING = auto()
    GAME_OVER = auto()


# ── Game state ─────────────────────────────────────────────

class State:
    def __init__(self):
        self.reset()

    def reset(self):
        mid = GRID // 2
        self.snake = deque([(mid, mid), (mid - 1, mid), (mid - 2, mid)])
        self.dir = RIGHT
        self.apple = None
        self.star = None
        self.star_ttl = 0
        self.score = 0
        self.growth = 0
        self.phase = Phase.WAITING
        self.queue = deque()
        self._place_apple()

    @property
    def speed_level(self):
        return self.score // 10 + 1

    @property
    def tps(self):
        return BASE_TPS + (self.speed_level - 1) * TPS_PER_LEVEL

    # ── Spawning ───────────────────────────────────────────

    def _free_cells(self):
        taken = set(self.snake)
        if self.apple:
            taken.add(self.apple)
        if self.star:
            taken.add(self.star)
        return [(x, y) for x in range(GRID) for y in range(GRID)
                if (x, y) not in taken]

    def _place_apple(self):
        free = self._free_cells()
        self.apple = random.choice(free) if free else None

    def _maybe_place_star(self):
        if self.star is not None or random.random() >= STAR_CHANCE:
            return
        free = self._free_cells()
        if free:
            self.star = random.choice(free)
            self.star_ttl = STAR_LIFE

    # ── Input ──────────────────────────────────────────────

    def enqueue(self, d):
        ref = self.queue[-1] if self.queue else self.dir
        if d != ref and d != OPPOSITE[ref]:
            self.queue.append(d)

    # ── Tick ───────────────────────────────────────────────

    def tick(self):
        if self.phase != Phase.PLAYING:
            return

        if self.queue:
            self.dir = self.queue.popleft()

        hx, hy = self.snake[0]
        dx, dy = self.dir
        head = (hx + dx, hy + dy)

        # wall
        if not (0 <= head[0] < GRID and 0 <= head[1] < GRID):
            self.phase = Phase.GAME_OVER
            return

        # self-collision (tail vacates if not growing)
        body = set(self.snake)
        if self.growth == 0:
            body.discard(self.snake[-1])
        if head in body:
            self.phase = Phase.GAME_OVER
            return

        self.snake.appendleft(head)

        # eat apple
        if head == self.apple:
            self.score += 1
            self.growth += 1
            self._place_apple()

        # eat star
        if self.star and head == self.star:
            self.score += 3
            self.growth += 3
            self.star = None
            self.star_ttl = 0

        # grow or shed tail
        if self.growth > 0:
            self.growth -= 1
        else:
            self.snake.pop()

        # star decay & spawn
        if self.star:
            self.star_ttl -= 1
            if self.star_ttl <= 0:
                self.star = None
        self._maybe_place_star()


# ── Rendering ──────────────────────────────────────────────

def cell_rect(x, y):
    return pygame.Rect(x * CELL + PAD, y * CELL + PAD,
                       CELL - 2 * PAD, CELL - 2 * PAD)


def star_poly(cx, cy, r_out, r_in, n=5):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def centered_text(surface, font, text, y):
    s = font.render(text, True, TEXT_CLR)
    surface.blit(s, (BOARD // 2 - s.get_width() // 2, y))


def draw(surface, state, font):
    surface.fill(BG)

    # grid
    for i in range(1, GRID):
        pygame.draw.line(surface, GRID_CLR, (i * CELL, 0), (i * CELL, BOARD))
        pygame.draw.line(surface, GRID_CLR, (0, i * CELL), (BOARD, i * CELL))

    # snake
    for i, (sx, sy) in enumerate(state.snake):
        clr = HEAD_CLR if i == 0 else BODY_CLR
        pygame.draw.rect(surface, clr, cell_rect(sx, sy), border_radius=8)

    # apple
    if state.apple:
        ax, ay = state.apple
        pygame.draw.circle(surface, APPLE_CLR,
                           (ax * CELL + CELL // 2, ay * CELL + CELL // 2),
                           CELL // 2 - PAD * 2)

    # star
    if state.star:
        sx, sy = state.star
        cx, cy = sx * CELL + CELL // 2, sy * CELL + CELL // 2
        r = CELL // 2 - PAD * 2
        pygame.draw.polygon(surface, STAR_CLR, star_poly(cx, cy, r, r * 0.4))

    # HUD
    score_s = font.render(f"Score: {state.score}", True, TEXT_CLR)
    speed_s = font.render(f"Speed: {state.speed_level}x", True, TEXT_CLR)
    surface.blit(score_s, (12, BOARD + 18))
    surface.blit(speed_s, (BOARD - speed_s.get_width() - 12, BOARD + 18))

    # overlays
    if state.phase in (Phase.WAITING, Phase.GAME_OVER):
        ov = pygame.Surface((BOARD, BOARD), pygame.SRCALPHA)
        ov.fill(OVERLAY_BG)
        surface.blit(ov, (0, 0))
        mid = BOARD // 2
        if state.phase == Phase.WAITING:
            centered_text(surface, font, "SNAKE", mid - 24)
            centered_text(surface, font, "Press ENTER to start", mid + 16)
        else:
            centered_text(surface, font, "GAME OVER", mid - 30)
            centered_text(surface, font, f"Score: {state.score}", mid + 10)
            centered_text(surface, font, "Press ENTER to play again", mid + 46)

    pygame.display.flip()


# ── Main loop ──────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 24, bold=True)
    state = State()
    tick_acc = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in KEYS and state.phase == Phase.PLAYING:
                    state.enqueue(KEYS[ev.key])
                elif ev.key == pygame.K_RETURN:
                    if state.phase == Phase.WAITING:
                        state.phase = Phase.PLAYING
                    elif state.phase == Phase.GAME_OVER:
                        state.reset()
                        state.phase = Phase.PLAYING

        if state.phase == Phase.PLAYING:
            tick_acc += dt
            interval = 1.0 / state.tps
            while tick_acc >= interval:
                tick_acc -= interval
                state.tick()

        draw(screen, state, font)


if __name__ == "__main__":
    main()
