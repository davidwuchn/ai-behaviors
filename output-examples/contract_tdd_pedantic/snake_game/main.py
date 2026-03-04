import sys

import pygame

from snake_game.board import TickResult
from snake_game.direction import Direction
from snake_game.game_state import GameState, Phase
from snake_game.input_queue import InputQueue

CELL_SIZE = 60
BOARD_SIZE = 8
WINDOW_SIZE = CELL_SIZE * BOARD_SIZE
HUD_HEIGHT = 40
WINDOW_WIDTH = WINDOW_SIZE
WINDOW_HEIGHT = WINDOW_SIZE + HUD_HEIGHT

COLOR_BG = (20, 20, 20)
COLOR_GRID = (40, 40, 40)
COLOR_SNAKE_HEAD = (0, 200, 0)
COLOR_SNAKE_BODY = (0, 150, 0)
COLOR_APPLE = (220, 30, 30)
COLOR_STAR = (255, 215, 0)
COLOR_TEXT = (220, 220, 220)
COLOR_HUD_BG = (30, 30, 30)

KEY_MAP = {
    pygame.K_w: Direction.UP,
    pygame.K_UP: Direction.UP,
    pygame.K_s: Direction.DOWN,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_a: Direction.LEFT,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_d: Direction.RIGHT,
    pygame.K_RIGHT: Direction.RIGHT,
}

TICK_EVENT = pygame.USEREVENT + 1


def draw_board(surface: pygame.Surface, game: GameState) -> None:
    surface.fill(COLOR_BG, (0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_SIZE))

    # Grid lines
    for x in range(BOARD_SIZE + 1):
        px = x * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID, (px, HUD_HEIGHT), (px, WINDOW_HEIGHT))
    for y in range(BOARD_SIZE + 1):
        py = y * CELL_SIZE + HUD_HEIGHT
        pygame.draw.line(surface, COLOR_GRID, (0, py), (WINDOW_WIDTH, py))

    # Snake
    for i, (x, y) in enumerate(game.board.snake):
        color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
        rect = pygame.Rect(x * CELL_SIZE + 1, y * CELL_SIZE + HUD_HEIGHT + 1,
                           CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(surface, color, rect)

    # Apple
    if game.board.apple is not None:
        ax, ay = game.board.apple
        center = (ax * CELL_SIZE + CELL_SIZE // 2,
                  ay * CELL_SIZE + HUD_HEIGHT + CELL_SIZE // 2)
        pygame.draw.circle(surface, COLOR_APPLE, center, CELL_SIZE // 2 - 2)

    # Star
    if game.board.star is not None:
        sx, sy = game.board.star
        draw_star_shape(surface, sx, sy)


def draw_star_shape(surface: pygame.Surface, gx: int, gy: int) -> None:
    """Draw a 5-pointed star in the given grid cell."""
    import math

    cx = gx * CELL_SIZE + CELL_SIZE // 2
    cy = gy * CELL_SIZE + HUD_HEIGHT + CELL_SIZE // 2
    outer_r = CELL_SIZE // 2 - 4
    inner_r = outer_r // 2
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = outer_r if i % 2 == 0 else inner_r
        points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    pygame.draw.polygon(surface, COLOR_STAR, points)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, game: GameState) -> None:
    surface.fill(COLOR_HUD_BG, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
    score_text = font.render(f"Score: {game.score}", True, COLOR_TEXT)
    speed_text = font.render(f"Speed: {game.speed}", True, COLOR_TEXT)
    surface.blit(score_text, (10, 8))
    surface.blit(speed_text, (WINDOW_WIDTH - speed_text.get_width() - 10, 8))


def draw_overlay(surface: pygame.Surface, font: pygame.font.Font, game: GameState) -> None:
    if game.phase == Phase.WAITING:
        text = "Press ENTER to start"
    elif game.phase == Phase.GAME_OVER:
        text = f"Game Over! Score: {game.score}  Press ENTER to restart"
    else:
        return

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (0, 0))

    rendered = font.render(text, True, COLOR_TEXT)
    x = (WINDOW_WIDTH - rendered.get_width()) // 2
    y = (WINDOW_HEIGHT - rendered.get_height()) // 2
    surface.blit(rendered, (x, y))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    font = pygame.font.SysFont("monospace", 22)
    clock = pygame.time.Clock()

    game = GameState()
    input_queue = InputQueue(Direction.RIGHT)

    pygame.time.set_timer(TICK_EVENT, game.tick_interval_ms())

    running = True
    current_direction = Direction.RIGHT

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP and game.phase == Phase.PLAYING:
                    input_queue.enqueue(KEY_MAP[event.key])

                if event.key == pygame.K_RETURN:
                    if game.phase in (Phase.WAITING, Phase.GAME_OVER):
                        game.start()
                        current_direction = Direction.RIGHT
                        input_queue.reset(Direction.RIGHT)
                        pygame.time.set_timer(TICK_EVENT, game.tick_interval_ms())

                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

            if event.type == TICK_EVENT and game.phase == Phase.PLAYING:
                # Pop next direction from queue, or use current
                next_dir = input_queue.pop()
                if next_dir is not None:
                    current_direction = next_dir

                result = game.tick(current_direction)

                if result == TickResult.DEATH:
                    pygame.time.set_timer(TICK_EVENT, 0)
                elif result in (TickResult.ATE_APPLE, TickResult.ATE_STAR):
                    pygame.time.set_timer(TICK_EVENT, game.tick_interval_ms())

        draw_board(screen, game)
        draw_hud(screen, font, game)
        draw_overlay(screen, font, game)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
