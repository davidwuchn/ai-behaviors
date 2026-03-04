import pygame
import random
import sys
from collections import deque

GRID = 8
CELL = 64
PADDING_TOP = 48
WIDTH = GRID * CELL
HEIGHT = GRID * CELL + PADDING_TOP

BG = (20, 20, 20)
GRID_COLOR = (40, 40, 40)
SNAKE_COLOR = (0, 200, 80)
SNAKE_HEAD_COLOR = (0, 255, 100)
APPLE_COLOR = (220, 30, 30)
STAR_COLOR = (255, 215, 0)
TEXT_COLOR = (220, 220, 220)
DIM_TEXT = (120, 120, 120)

DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

OPPOSITES = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

BASE_SPEED = 5
SPEED_INCREMENT = 1


def random_free_cell(occupied):
    free = [(x, y) for x in range(GRID) for y in range(GRID) if (x, y) not in occupied]
    return random.choice(free) if free else None


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        mid = GRID // 2
        self.snake = deque([(mid - 2, mid), (mid - 1, mid), (mid, mid)])
        self.direction = "RIGHT"
        self.input_queue = deque()
        self.score = 0
        self.speed = BASE_SPEED
        self.alive = True
        self.turn = 0

        self.apple = None
        self.star = None
        self.star_timer = 0
        self.spawn_apple()

    def spawn_apple(self):
        occupied = set(self.snake)
        if self.star:
            occupied.add(self.star)
        self.apple = random_free_cell(occupied)

    def spawn_star(self):
        if self.star is not None:
            return
        occupied = set(self.snake)
        occupied.add(self.apple)
        cell = random_free_cell(occupied)
        if cell:
            self.star = cell
            self.star_timer = 20

    def queue_direction(self, new_dir):
        # Determine what direction the snake would be facing after all queued moves
        effective = self.direction
        for d in self.input_queue:
            effective = d
        if new_dir == OPPOSITES.get(effective):
            return
        if new_dir == effective:
            return
        self.input_queue.append(new_dir)

    def step(self):
        if not self.alive:
            return

        if self.input_queue:
            self.direction = self.input_queue.popleft()

        dx, dy = DIRECTIONS[self.direction]
        hx, hy = self.snake[-1]
        nx, ny = hx + dx, hy + dy

        # Wall collision
        if nx < 0 or nx >= GRID or ny < 0 or ny >= GRID:
            self.alive = False
            return

        # Self collision
        if (nx, ny) in set(self.snake):
            self.alive = False
            return

        self.snake.append((nx, ny))
        self.turn += 1

        grow = 0
        if (nx, ny) == self.apple:
            grow = 1
            self.score += 1
        if self.star and (nx, ny) == self.star:
            grow += 3
            self.score += 3
            self.star = None
            self.star_timer = 0

        if grow == 0:
            self.snake.popleft()
        else:
            # Keep the tail; only remove if we need fewer growth
            for _ in range(grow - 1):
                # Duplicate the tail to grow
                self.snake.appendleft(self.snake[0])

        if (nx, ny) == self.apple:
            self.spawn_apple()

        # Star timer
        if self.star is not None:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star = None

        # Maybe spawn star (~10% chance per turn if none exists)
        if self.star is None and random.random() < 0.10:
            self.spawn_star()

        # Speed increases every 10 points
        self.speed = BASE_SPEED + (self.score // 10) * SPEED_INCREMENT


def draw_star_shape(surface, cx, cy, radius, color):
    """Draw a 5-pointed star."""
    import math

    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius if i % 2 == 0 else radius * 0.4
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)


def draw(screen, font, game, state):
    screen.fill(BG)

    # Draw grid
    for x in range(GRID + 1):
        pygame.draw.line(screen, GRID_COLOR, (x * CELL, PADDING_TOP), (x * CELL, HEIGHT))
    for y in range(GRID + 1):
        pygame.draw.line(screen, GRID_COLOR, (0, y * CELL + PADDING_TOP), (WIDTH, y * CELL + PADDING_TOP))

    # HUD
    score_surf = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    speed_surf = font.render(f"Speed: {game.speed}", True, TEXT_COLOR)
    screen.blit(score_surf, (8, 12))
    screen.blit(speed_surf, (WIDTH - speed_surf.get_width() - 8, 12))

    # Apple
    if game.apple:
        ax, ay = game.apple
        center = (ax * CELL + CELL // 2, ay * CELL + CELL // 2 + PADDING_TOP)
        pygame.draw.circle(screen, APPLE_COLOR, center, CELL // 2 - 6)

    # Star
    if game.star:
        sx, sy = game.star
        cx = sx * CELL + CELL // 2
        cy = sy * CELL + CELL // 2 + PADDING_TOP
        draw_star_shape(screen, cx, cy, CELL // 2 - 6, STAR_COLOR)

    # Snake
    for i, (sx, sy) in enumerate(game.snake):
        rect = pygame.Rect(sx * CELL + 2, sy * CELL + PADDING_TOP + 2, CELL - 4, CELL - 4)
        color = SNAKE_HEAD_COLOR if i == len(game.snake) - 1 else SNAKE_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=6)

    # Overlays
    if state == "waiting":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        msg = font.render("Press ENTER to start", True, TEXT_COLOR)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
    elif state == "dead":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        msg1 = font.render(f"Game Over!  Score: {game.score}", True, TEXT_COLOR)
        msg2 = font.render("Press ENTER to restart", True, DIM_TEXT)
        screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()


KEY_MAP = {
    pygame.K_w: "UP",
    pygame.K_UP: "UP",
    pygame.K_s: "DOWN",
    pygame.K_DOWN: "DOWN",
    pygame.K_a: "LEFT",
    pygame.K_LEFT: "LEFT",
    pygame.K_d: "RIGHT",
    pygame.K_RIGHT: "RIGHT",
}


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 22, bold=True)

    game = Game()
    state = "waiting"  # waiting | playing | dead

    tick_timer = 0

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if state in ("waiting", "dead"):
                        game.reset()
                        state = "playing"
                        tick_timer = 0
                elif event.key in KEY_MAP and state == "playing":
                    game.queue_direction(KEY_MAP[event.key])

        if state == "playing":
            tick_timer += dt
            interval = 1000 / game.speed
            while tick_timer >= interval:
                tick_timer -= interval
                game.step()
                if not game.alive:
                    state = "dead"
                    break

        draw(screen, font, game, state)


if __name__ == "__main__":
    main()
