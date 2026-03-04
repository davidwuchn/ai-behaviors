import pygame
import sys
from game import Game, Direction

CELL = 60
BOARD = Game.BOARD_SIZE
WINDOW = CELL * BOARD
HUD_HEIGHT = 40
SCREEN_W = WINDOW
SCREEN_H = WINDOW + HUD_HEIGHT

BG = (30, 30, 30)
GRID = (50, 50, 50)
SNAKE_COLOR = (0, 200, 80)
HEAD_COLOR = (0, 255, 100)
APPLE_COLOR = (220, 30, 30)
STAR_COLOR = (255, 220, 50)
TEXT_COLOR = (220, 220, 220)

KEY_MAP = {
    pygame.K_w: Direction.UP, pygame.K_UP: Direction.UP,
    pygame.K_s: Direction.DOWN, pygame.K_DOWN: Direction.DOWN,
    pygame.K_a: Direction.LEFT, pygame.K_LEFT: Direction.LEFT,
    pygame.K_d: Direction.RIGHT, pygame.K_RIGHT: Direction.RIGHT,
}

BASE_FPS = 5


def draw(screen, font, game, state):
    screen.fill(BG)

    # Grid
    for i in range(1, BOARD):
        pygame.draw.line(screen, GRID, (i * CELL, 0), (i * CELL, WINDOW))
        pygame.draw.line(screen, GRID, (0, i * CELL), (WINDOW, i * CELL))

    # Apple
    if game.apple:
        r = pygame.Rect(game.apple[0] * CELL + 4, game.apple[1] * CELL + 4, CELL - 8, CELL - 8)
        pygame.draw.ellipse(screen, APPLE_COLOR, r)

    # Star
    if game.star:
        cx = game.star[0] * CELL + CELL // 2
        cy = game.star[1] * CELL + CELL // 2
        draw_star_shape(screen, cx, cy, CELL // 2 - 4)

    # Snake
    for i, (x, y) in enumerate(game.snake):
        color = HEAD_COLOR if i == 0 else SNAKE_COLOR
        pygame.draw.rect(screen, color, (x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4), border_radius=6)

    # HUD
    hud_y = WINDOW + 4
    score_text = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    speed_text = font.render(f"Speed: {game.speed}", True, TEXT_COLOR)
    screen.blit(score_text, (10, hud_y))
    screen.blit(speed_text, (SCREEN_W - speed_text.get_width() - 10, hud_y))

    # Overlay messages
    if state == "waiting":
        draw_centered(screen, font, "Press ENTER to start")
    elif state == "dead":
        draw_centered(screen, font, f"Game Over! Score: {game.score}")
        draw_centered(screen, font, "Press ENTER to restart", offset=30)

    pygame.display.flip()


def draw_centered(screen, font, text, offset=0):
    surf = font.render(text, True, TEXT_COLOR)
    x = (SCREEN_W - surf.get_width()) // 2
    y = (WINDOW - surf.get_height()) // 2 + offset
    # Background rect for readability
    bg = pygame.Surface((surf.get_width() + 16, surf.get_height() + 8))
    bg.set_alpha(180)
    bg.fill((0, 0, 0))
    screen.blit(bg, (x - 8, y - 4))
    screen.blit(surf, (x, y))


def draw_star_shape(screen, cx, cy, r):
    import math
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.4
        points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    pygame.draw.polygon(screen, STAR_COLOR, points)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Snake")
    font = pygame.font.SysFont(None, 28)
    clock = pygame.time.Clock()

    game = Game()
    state = "waiting"  # waiting | playing | dead

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if state == "waiting":
                        state = "playing"
                    elif state == "dead":
                        game = Game()
                        state = "playing"
                elif state == "playing" and event.key in KEY_MAP:
                    game.queue_direction(KEY_MAP[event.key])

        if state == "playing":
            game.tick()
            if not game.alive:
                state = "dead"
            else:
                game.maybe_spawn_star()

        draw(screen, font, game, state)
        clock.tick(BASE_FPS + (game.speed - 1) * 2)


if __name__ == "__main__":
    main()
