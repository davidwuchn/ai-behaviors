#!/usr/bin/env python3
import math
import random
import sys
from collections import deque

import pygame

GRID = 8
CELL = 80
BOARD = GRID * CELL
HUD = 60
WIDTH = BOARD
HEIGHT = BOARD + HUD

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
KEY_DIR = {
    pygame.K_w: UP, pygame.K_UP: UP,
    pygame.K_s: DOWN, pygame.K_DOWN: DOWN,
    pygame.K_a: LEFT, pygame.K_LEFT: LEFT,
    pygame.K_d: RIGHT, pygame.K_RIGHT: RIGHT,
}

BG       = (15, 15, 15)
GRID_A   = (25, 25, 30)
GRID_B   = (30, 30, 35)
HEAD_COL = (100, 220, 100)
BODY_COL = (60, 170, 60)
APPLE    = (220, 50, 50)
STAR     = (255, 210, 40)
TEXT     = (210, 210, 210)
DIM      = (110, 110, 110)
OVERLAY  = (0, 0, 0, 160)
HUD_BG   = (20, 20, 20)


class Snake:
    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 30, bold=True)
        self.sfont = pygame.font.SysFont("monospace", 22)
        self.reset()

    def reset(self):
        m = GRID // 2
        self.body = deque([(m, m), (m - 1, m), (m - 2, m)])
        self.dir = RIGHT
        self.queue = deque()
        self.score = 0
        self.grow = 0
        self.apple = None
        self.star = None
        self.star_ttl = 0
        self.alive = True
        self.started = False
        self._spawn_apple()

    def _free(self):
        occ = set(self.body)
        if self.apple:
            occ.add(self.apple)
        if self.star:
            occ.add(self.star)
        return [
            (x, y)
            for x in range(GRID)
            for y in range(GRID)
            if (x, y) not in occ
        ]

    def _spawn_apple(self):
        f = self._free()
        self.apple = random.choice(f) if f else None

    def _spawn_star(self):
        f = self._free()
        if f:
            self.star = random.choice(f)
            self.star_ttl = 20

    @property
    def speed(self):
        return self.score // 10 + 1

    @property
    def interval(self):
        return max(80, 300 - (self.speed - 1) * 25)

    def enqueue(self, key):
        if key not in KEY_DIR:
            return
        d = KEY_DIR[key]
        prev = self.queue[-1] if self.queue else self.dir
        if d != OPPOSITE[prev] and d != prev:
            self.queue.append(d)

    def tick(self):
        if self.queue:
            self.dir = self.queue.popleft()

        hx, hy = self.body[0]
        nh = (hx + self.dir[0], hy + self.dir[1])

        if not (0 <= nh[0] < GRID and 0 <= nh[1] < GRID):
            self.alive = False
            return

        eat_a = nh == self.apple
        eat_s = self.star is not None and nh == self.star
        if eat_a:
            self.grow += 1
        if eat_s:
            self.grow += 3

        check = set(self.body)
        if self.grow == 0:
            check.discard(self.body[-1])
        if nh in check:
            self.alive = False
            return

        self.body.appendleft(nh)
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()

        if eat_a:
            self.score += 1
            self._spawn_apple()
        if eat_s:
            self.score += 3
            self.star = None
            self.star_ttl = 0

        if self.star is not None:
            self.star_ttl -= 1
            if self.star_ttl <= 0:
                self.star = None
        elif random.random() < 0.08:
            self._spawn_star()

    def _cell_rect(self, x, y, shrink=3):
        return pygame.Rect(
            x * CELL + shrink, y * CELL + shrink,
            CELL - 2 * shrink, CELL - 2 * shrink,
        )

    def _draw_star_shape(self, x, y):
        cx = x * CELL + CELL // 2
        cy = y * CELL + CELL // 2
        r_out = CELL // 2 - 10
        r_in = r_out * 0.42
        pts = []
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        pygame.draw.polygon(self.scr, STAR, pts)

    def draw(self):
        self.scr.fill(BG)

        for x in range(GRID):
            for y in range(GRID):
                c = GRID_A if (x + y) % 2 == 0 else GRID_B
                pygame.draw.rect(self.scr, c, pygame.Rect(x * CELL, y * CELL, CELL, CELL))

        if self.apple:
            cx = self.apple[0] * CELL + CELL // 2
            cy = self.apple[1] * CELL + CELL // 2
            pygame.draw.circle(self.scr, APPLE, (cx, cy), CELL // 2 - 8)

        if self.star:
            self._draw_star_shape(*self.star)

        for i, seg in enumerate(self.body):
            c = HEAD_COL if i == 0 else BODY_COL
            pygame.draw.rect(self.scr, c, self._cell_rect(*seg), border_radius=8)

        pygame.draw.rect(self.scr, HUD_BG, pygame.Rect(0, BOARD, WIDTH, HUD))
        y = BOARD + 14
        s1 = self.font.render(f"Score: {self.score}", True, TEXT)
        s2 = self.font.render(f"Speed: {self.speed}", True, TEXT)
        self.scr.blit(s1, (12, y))
        self.scr.blit(s2, (WIDTH - s2.get_width() - 12, y))

        if not self.started:
            self._overlay("SNAKE", "Press ENTER to start")
        elif not self.alive:
            self._overlay("GAME OVER", f"Score: {self.score}  |  ENTER to restart")

        pygame.display.flip()

    def _overlay(self, title, sub):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill(OVERLAY)
        self.scr.blit(s, (0, 0))
        t = self.font.render(title, True, TEXT)
        u = self.sfont.render(sub, True, DIM)
        self.scr.blit(t, ((WIDTH - t.get_width()) // 2, HEIGHT // 2 - 28))
        self.scr.blit(u, ((WIDTH - u.get_width()) // 2, HEIGHT // 2 + 10))

    def run(self):
        TICK = pygame.USEREVENT + 1
        pygame.time.set_timer(TICK, self.interval)

        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        if not self.started:
                            self.started = True
                            pygame.time.set_timer(TICK, self.interval)
                        elif not self.alive:
                            self.reset()
                            self.started = True
                            pygame.time.set_timer(TICK, self.interval)
                    elif self.started and self.alive:
                        self.enqueue(ev.key)
                if ev.type == TICK and self.started and self.alive:
                    prev_spd = self.speed
                    self.tick()
                    if self.speed != prev_spd:
                        pygame.time.set_timer(TICK, self.interval)

            self.draw()
            self.clock.tick(60)


if __name__ == "__main__":
    Snake().run()
