import sys
import pygame
from dataclasses import replace
from random import Random

from game import (
    GameState, initial_state, tick, speed, level,
    enqueue_direction, resolve_direction, project_path,
    UP, DOWN, LEFT, RIGHT, BOARD_SIZE,
)

CELL = 60
PANEL = 40
WINDOW = CELL * BOARD_SIZE

BG = (30, 30, 30)
GRID = (40, 40, 40)
SNAKE_HEAD = (0, 220, 0)
SNAKE_BODY = (0, 160, 0)
APPLE = (220, 30, 30)
STAR = (255, 215, 0)
STAR_FADING = (255, 100, 0)
GHOST = (0, 120, 0)
GHOST_FATAL = (180, 40, 40)
COLLISION = (255, 60, 200)
TEXT = (220, 220, 220)

KEY_MAP = {
    pygame.K_w: UP, pygame.K_UP: UP,
    pygame.K_s: DOWN, pygame.K_DOWN: DOWN,
    pygame.K_a: LEFT, pygame.K_LEFT: LEFT,
    pygame.K_d: RIGHT, pygame.K_RIGHT: RIGHT,
}


def draw_cell(surface, x, y, color):
    rect = pygame.Rect(x * CELL + 1, y * CELL + PANEL + 1, CELL - 2, CELL - 2)
    pygame.draw.rect(surface, color, rect)


def draw_cell_outline(surface, x, y, color):
    rect = pygame.Rect(x * CELL + 1, y * CELL + PANEL + 1, CELL - 2, CELL - 2)
    pygame.draw.rect(surface, color, rect, 3)


def draw(surface, state, font, queue):
    surface.fill(BG)

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            draw_cell(surface, x, y, GRID)

    # Ghost trail (queued moves)
    if state.phase == "playing" and queue:
        snake_set = set(state.snake)
        for gx, gy in project_path(state.snake[0], queue):
            if 0 <= gx < BOARD_SIZE and 0 <= gy < BOARD_SIZE:
                color = GHOST_FATAL if (gx, gy) in snake_set else GHOST
                draw_cell_outline(surface, gx, gy, color)

    for i, cell in enumerate(state.snake):
        draw_cell(surface, cell[0], cell[1], SNAKE_HEAD if i == 0 else SNAKE_BODY)

    draw_cell(surface, state.apple[0], state.apple[1], APPLE)

    if state.star is not None:
        color = STAR_FADING if state.star_timer <= 5 else STAR
        draw_cell(surface, state.star[0], state.star[1], color)

    # Collision point highlight
    if state.phase == "lose" and state.death == "self":
        hx, hy = state.snake[0]
        dx, dy = state.direction
        draw_cell(surface, hx + dx, hy + dy, COLLISION)

    lvl = level(state.score)
    score_text = font.render(f"Score: {state.score}  Level: {lvl}", True, TEXT)
    surface.blit(score_text, (10, 10))

    if state.phase in ("start", "win", "lose"):
        overlay = pygame.Surface((WINDOW, WINDOW + PANEL), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        if state.phase == "start":
            msg = "Press ENTER to start"
        elif state.phase == "win":
            msg = f"You win!  Score: {state.score}.  ENTER to restart"
        else:
            cause = "Hit wall!" if state.death == "wall" else "Hit self!"
            msg = f"{cause}  Score: {state.score}.  ENTER to restart"

        text = font.render(msg, True, TEXT)
        surface.blit(text, text.get_rect(center=(WINDOW // 2, (WINDOW + PANEL) // 2)))

    pygame.display.flip()


def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW, WINDOW + PANEL))
    pygame.display.set_caption("Snake")
    font = pygame.font.Font(None, 28)
    clock = pygame.time.Clock()

    rng = Random()
    state = initial_state(rng)
    queue = []
    tick_accum = 0

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP and state.phase == "playing":
                    enqueue_direction(queue, KEY_MAP[event.key], state.direction)
                elif event.key == pygame.K_RETURN:
                    if state.phase == "start":
                        state = replace(state, phase="playing")
                        queue.clear()
                        tick_accum = 0
                    elif state.phase in ("win", "lose"):
                        state = replace(initial_state(rng), phase="playing")
                        queue.clear()
                        tick_accum = 0

        if state.phase == "playing":
            interval = 1000 // speed(state.score)
            tick_accum += min(dt, interval)
            while state.phase == "playing":
                interval = 1000 // speed(state.score)
                if tick_accum < interval:
                    break
                tick_accum -= interval
                direction = resolve_direction(queue, state.direction)
                state = replace(state, direction=direction)
                state = tick(state, rng)

        draw(surface, state, font, queue)


if __name__ == "__main__":
    main()
