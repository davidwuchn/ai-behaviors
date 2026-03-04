import pygame
import random
import sys
from collections import deque

CELL = 60
COLS, ROWS = 8, 8
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL
HEADER = 40
WINDOW_HEIGHT = HEIGHT + HEADER

BG = (20, 20, 20)
GRID_COLOR = (35, 35, 35)
SNAKE_COLOR = (0, 200, 80)
SNAKE_HEAD_COLOR = (0, 255, 100)
APPLE_COLOR = (220, 30, 30)
STAR_COLOR = (255, 215, 0)
TEXT_COLOR = (220, 220, 220)

DIR = {"right": (1, 0), "left": (-1, 0), "up": (0, -1), "down": (0, 1)}
OPPOSITES = {"right": "left", "left": "right", "up": "down", "down": "up"}

KEY_MAP = {
    pygame.K_w: "up", pygame.K_UP: "up",
    pygame.K_s: "down", pygame.K_DOWN: "down",
    pygame.K_a: "left", pygame.K_LEFT: "left",
    pygame.K_d: "right", pygame.K_RIGHT: "right",
}


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        mid_y = ROWS // 2
        mid_x = COLS // 2
        self.snake = deque([(mid_x - 2, mid_y), (mid_x - 1, mid_y), (mid_x, mid_y)])
        self.direction = "right"
        self.input_queue = deque()
        self.score = 0
        self.speed_level = 1
        self.tick_rate = 5
        self.apple = None
        self.star = None
        self.star_timer = 0
        self.grow = 0
        self.alive = True
        self.place_apple()

    def occupied(self):
        return set(self.snake)

    def place_apple(self):
        taken = self.occupied()
        if self.star:
            taken.add(self.star)
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in taken]
        if free:
            self.apple = random.choice(free)

    def maybe_spawn_star(self):
        if self.star is not None:
            return
        if random.random() < 0.05:
            taken = self.occupied()
            taken.add(self.apple)
            free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in taken]
            if free:
                self.star = random.choice(free)
                self.star_timer = 20

    def effective_direction(self):
        """Return the current direction after accounting for the last resolved input."""
        return self.direction

    def queue_input(self, new_dir):
        # Determine what direction would be "current" after all queued inputs resolve
        last_dir = self.direction
        for d in self.input_queue:
            last_dir = d
        if new_dir == last_dir or new_dir == OPPOSITES.get(last_dir):
            return
        self.input_queue.append(new_dir)

    def step(self):
        if not self.alive:
            return

        if self.input_queue:
            desired = self.input_queue.popleft()
            if desired != OPPOSITES.get(self.direction):
                self.direction = desired

        dx, dy = DIR[self.direction]
        hx, hy = self.snake[-1]
        nx, ny = hx + dx, hy + dy

        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            self.alive = False
            return

        if (nx, ny) in self.occupied():
            self.alive = False
            return

        self.snake.append((nx, ny))

        ate_apple = (nx, ny) == self.apple
        ate_star = self.star and (nx, ny) == self.star

        if ate_apple:
            self.score += 1
            self.grow += 1
            self.place_apple()
        if ate_star:
            self.score += 3
            self.grow += 3
            self.star = None
            self.star_timer = 0

        if self.grow > 0:
            self.grow -= 1
        else:
            self.snake.popleft()

        # Speed increases every 10 points
        new_level = 1 + self.score // 10
        if new_level != self.speed_level:
            self.speed_level = new_level
            self.tick_rate = min(5 + (self.speed_level - 1) * 2, 20)

        # Star timer
        if self.star is not None:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star = None

        self.maybe_spawn_star()


def draw(screen, font, game, state):
    screen.fill(BG)

    # Draw grid
    for x in range(COLS):
        for y in range(ROWS):
            rect = pygame.Rect(x * CELL, HEADER + y * CELL, CELL, CELL)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    # Draw apple
    if game.apple:
        ax, ay = game.apple
        center = (ax * CELL + CELL // 2, HEADER + ay * CELL + CELL // 2)
        pygame.draw.circle(screen, APPLE_COLOR, center, CELL // 2 - 4)

    # Draw star
    if game.star:
        sx, sy = game.star
        cx = sx * CELL + CELL // 2
        cy = HEADER + sy * CELL + CELL // 2
        draw_star_shape(screen, cx, cy, CELL // 2 - 4)

    # Draw snake
    for i, (sx, sy) in enumerate(game.snake):
        rect = pygame.Rect(sx * CELL + 2, HEADER + sy * CELL + 2, CELL - 4, CELL - 4)
        color = SNAKE_HEAD_COLOR if i == len(game.snake) - 1 else SNAKE_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=6)

    # Header
    score_surf = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    speed_surf = font.render(f"Speed: {game.speed_level}", True, TEXT_COLOR)
    screen.blit(score_surf, (10, 8))
    screen.blit(speed_surf, (WIDTH - speed_surf.get_width() - 10, 8))

    if state == "waiting":
        draw_overlay(screen, font, "SNAKE", "Press ENTER to start")
    elif state == "dead":
        draw_overlay(screen, font, f"Game Over  -  Score: {game.score}", "Press ENTER to restart")

    pygame.display.flip()


def draw_overlay(screen, font, title, subtitle):
    overlay = pygame.Surface((WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("monospace", 36, bold=True)
    title_surf = big_font.render(title, True, (255, 255, 255))
    sub_surf = font.render(subtitle, True, (180, 180, 180))
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, WINDOW_HEIGHT // 2 - 30))
    screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, WINDOW_HEIGHT // 2 + 20))


def draw_star_shape(screen, cx, cy, r):
    import math
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.45
        points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    pygame.draw.polygon(screen, STAR_COLOR, points)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 18)

    game = Game()
    state = "waiting"  # waiting | playing | dead
    tick_acc = 0

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if state == "waiting":
                        state = "playing"
                    elif state == "dead":
                        game.reset()
                        state = "playing"
                elif state == "playing" and event.key in KEY_MAP:
                    game.queue_input(KEY_MAP[event.key])

        if state == "playing":
            tick_acc += dt
            interval = 1000 / game.tick_rate
            while tick_acc >= interval:
                tick_acc -= interval
                game.step()
                if not game.alive:
                    state = "dead"
                    break

        draw(screen, font, game, state)


if __name__ == "__main__":
    main()
